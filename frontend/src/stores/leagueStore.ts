// stores/leagueStore.ts
import { defineStore } from 'pinia';
import { computed, ref, shallowRef } from 'vue';
import { fetchLeagueDetails } from 'src/services/leagueService';
import { useUserStore } from 'stores/userStore';
import { api } from 'boot/axios';
import { TMatchResult, TLeagueMemberDto, TLeagueDto, TLeagueStatus } from 'src/types';


/**
 * Represents a Vue Store for managing league-related data and state.
 *
 * This store is responsible for fetching, maintaining, and providing access to
 * primaryrmation about leagues, their members, games, statuses, and match results.
 *
 * A range of state properties, computed values, and actions are provided to
 * manage or derive data associated with leagues.
 *
 * The store provides comprehensive utilities including:
 * - State variables for holding league primary, members, and match results.
 * - Computed properties for efficient access to specific structured data.
 * - Actions for initialization, data fetching, and updates.
 *
 * Key Features:
 * - Reactive state management for leagues and members.
 * - Efficient mapping and lookup utilities for member and game data.
 * - Result management for games using immutable updates for reactivity.
 */
export const useLeagueStore = (id: number) => {
  return defineStore(`league-${id}`, () => {
    const loading = ref(false);

    // leagueData
    const leagueId = ref(id);
    const leagueData = shallowRef<TLeagueDto|null>(null);
    const members = ref<TLeagueMemberDto[]>([]);
    const leagueStatus = ref<TLeagueStatus>('PICKING'); // states: PICKING, BANNING, REPICKING, PLAYING, DONE

    const statusMap: Record<TLeagueStatus, { noun?: string; verb?: string }> = {
      PICKING: { noun: 'Game Selection Phase', verb: 'pick' },
      REPICKING: { noun: 'Game Reselection', verb: 'pick again' },
      BANNING: { noun: 'Ban Phase', verb: 'ban' },
      PLAYING: { noun: 'Games running' },
      DONE: { noun: 'League finished' },
    };

    const statusNoun = computed(
      () => statusMap[leagueStatus.value]?.noun ?? ''
    );
    const statusVerb = computed(() => statusMap[leagueStatus.value]?.verb ?? '');

    // --- Derived maps for O(1) lookups ---
    const membersById = computed<{ [key: number]: TLeagueMemberDto }>(() =>
      members.value.reduce((acc: { [key: number]: TLeagueMemberDto }, m) => {
        acc[m.id] = m;
        return acc;
      }, {})
    );

    const selectedGames = computed(() => {
      if (!members.value.length) return [];

      return members.value
        .flatMap((member) => {
          if (!member.selected_games) return [];
          return member.selected_games.map((game) => ({
            ...game,
            selected_by: member.username,
          })) as (TSelectedGameDto & { selected_by: string })[];
        })
        .filter((game) => game !== null && game !== undefined);
    });

    const selectedGamesById = computed<
      Record<number, TSelectedGameDto & { selected_by: string }>
    >(() =>
      selectedGames.value.reduce(
        (acc, g) => {
          acc[g.id] = g;
          return acc;
        },
        {} as Record<number, TSelectedGameDto & { selected_by: string }>
      )
    );

    // --- Results keyed by selected_game for fast access ---
    // Using a Record so reactivity stays simple.
    const matchResultsBySelectedGame = ref<Record<number, TMatchResult[]>>({});

    const matchResults = computed<TMatchResult[]>(() =>
      Object.values(matchResultsBySelectedGame.value).flat()
    );

    const selectedGamesWithResults = computed(() =>
      selectedGames.value.filter(g => (matchResultsBySelectedGame.value[g.id]?.length ?? 0) > 0)
    );

    const selectedGamesFetchedEmpty = computed(() =>
      selectedGames.value.filter(g => (matchResultsBySelectedGame.value[g.id]?.length ?? 0) === 0)
    );


    const initialized = ref(false);
    let initPromise: Promise<void> | null = null;

    async function updateLeagueData() {
      if (leagueId.value == null) return;
      await new Promise(resolve => setTimeout(resolve, 1000));
      loading.value = true;
      try {
        const data = await fetchLeagueDetails(leagueId.value);
        leagueData.value = data;
        members.value = data.members;
        leagueStatus.value = data.status;
      } finally {
        loading.value = false;
      }
    }

    // Helper to set results atomically & dedup on id
    function setResultsForGame(selectedGameId: number, results: TMatchResult[]) {
      const uniq = new Map<number, TMatchResult>();
      results.forEach(r => uniq.set(r.id, r));
      matchResultsBySelectedGame.value = {
        ...matchResultsBySelectedGame.value,
        [selectedGameId]: Array.from(uniq.values()).sort((a, b) => (b.points ?? 0) - (a.points ?? 0)),
      };
    }

    async function getMatchResults() {
      if (leagueId.value == null) return;
      const ids = selectedGames.value.map((s) => s.id);
      if (!ids.length) return;

      loading.value = true;
      try {
        const promises = ids.map((id) =>
          api.get<TMatchResult[]>(`/result/results/?selected_game=${id}`)
            .then(({ data }) => setResultsForGame(id, data))
            .catch(() => setResultsForGame(id, []))
        );
        await Promise.all(promises);
      } finally {
        loading.value = false;
      }
    }

    async function refreshResultsForGame(selectedGameId: number) {
      loading.value = true;
      try {
        const { data } = await api.get<TMatchResult[]>(`/result/results/?selected_game=${selectedGameId}`);
        setResultsForGame(selectedGameId, data);
      } finally {
        loading.value = false;
      }
    }

    function hasSelectedGameResult(selectedGameId: number) {
      return matchResultsBySelectedGame.value[selectedGameId]?.length > 0;
    }

    async function init() {
      if (initialized.value) return;
      if (initPromise) return initPromise;
      loading.value = true;
      initPromise = (async () => {
        try {
          await updateLeagueData();
          await getMatchResults();
          initialized.value = true;
        } finally {
          loading.value = false;
          initPromise = null;
        }
      })();

      return initPromise;
    }

    const activePlayer = computed(() =>
      members.value.find((m) => m.is_active_player)
    );

    const { isMe } = useUserStore();
    const isMeActivePlayer = computed(() =>
      activePlayer.value ? isMe(activePlayer.value.username) : false
    );

    const myProfileId = computed(
      () => members.value.find((m) => isMe(m.username))?.profile
    );

    const isMePickingGame = computed(
      () => (leagueStatus.value === 'PICKING' || leagueStatus.value === 'REPICKING') && isMeActivePlayer.value
    );
    const isMeBanningGame = computed(
      () => leagueStatus.value === 'BANNING' && isMeActivePlayer.value
    );

    void init();

    return {
      // state
      loading,
      leagueId,
      leagueData,
      members,
      leagueStatus,
      initialized,
      selectedGames,
      matchResults,
      matchResultsBySelectedGame,

      // getters
      activePlayer,
      isMeActivePlayer,
      isMePickingGame,
      isMeBanningGame,
      myProfileId,
      selectedGamesWithResults,
      selectedGamesFetchedEmpty,
      membersById,
      selectedGamesById,
      statusNoun,
      statusVerb,


      // actions
      updateLeagueData,
      refreshResultsForGame,
      hasSelectedGameResult,
    };
  });
}

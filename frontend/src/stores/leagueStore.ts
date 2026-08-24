// stores/leagueStore.ts
import { defineStore } from 'pinia';
import { computed, ref, shallowRef } from 'vue';
import { fetchLeagueDetails } from 'src/services/leagueService';
import { useUserStore } from 'stores/userStore';
import { api } from 'boot/axios';
import {
  TSeasonParticipantDto,
  TLeagueDto,
  TLeagueStatus,
  TSelectedGameDto,
  TMatchResult,
} from 'src/types';


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
    const members = ref<TSeasonParticipantDto[]>([]);
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
    const membersById = computed<{ [key: number]: TSeasonParticipantDto }>(() =>
      members.value.reduce((acc: { [key: number]: TSeasonParticipantDto }, m) => {
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
      selectedGames.value.filter(
        (g) =>
          (matchResultsBySelectedGame.value[g.id]?.length ?? 0) === 0 &&
          !g.successfully_banned
      )
    );


    const initialized = ref(false);
    // Background refresh indicator (does not block UI, unlike `loading`).
    const refreshing = ref(false);
    let initPromise: Promise<void> | null = null;
    let refreshPromise: Promise<void> | null = null;

    /**
     * Fetch league details from the backend and merge them into the store.
     *
     * By default this sets the blocking `loading` flag so the UI can show a
     * spinner while there is nothing to display yet. When called as a
     * background refresh (`{ background: true }`) it uses the non-blocking
     * `refreshing` flag instead, so cached store data stays visible while the
     * fresh data is being fetched (stale-while-revalidate).
     */
    async function updateLeagueData(options: { background?: boolean } = {}) {
      if (leagueId.value == null) return;
      const background = options.background === true;
      const flag = background ? refreshing : loading;
      flag.value = true;
      try {
        const data = await fetchLeagueDetails(leagueId.value);
        leagueData.value = data;
        members.value = data.members || [];
        leagueStatus.value = data.status || 'PICKING';

        // Populate matchResultsBySelectedGame from the prefetched data
        (data.members || []).forEach(member => {
          (member.selected_games || []).forEach(selGame => {
            if (selGame.results) {
              setResultsForGame(selGame.id, selGame.results);
            }
          });
        });

        // Keep the user store in sync so navbar indicators (e.g. "my turn"
        // bubble on the My League button) reflect the latest league state.
        await useUserStore().setMyCurrentLeagueId();
      } finally {
        flag.value = false;
      }
    }

    async function refresh() {
      await updateLeagueData();
      await getMatchResults();
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

    /**
     * Stale-while-revalidate initialization.
     *
     * - First ever call for this league: fetch synchronously with the blocking
     *   `loading` flag, so consumers can `await init()` and then render.
     * - Subsequent calls (store already has data): return immediately using the
     *   cached data from the store, and kick off a non-blocking background
     *   refresh so any changes propagate reactively without a visible loading
     *   state. This is the key to minimizing perceived loading times when
     *   navigating back to a league page.
     */
    async function init() {
      // If we already have cached league data in the store, use it immediately
      // and refresh in the background.
      if (initialized.value && leagueData.value) {
        void refreshInBackground();
        return;
      }
      // In-flight initial fetch — reuse the same promise for concurrent callers.
      if (initPromise) return initPromise;

      initPromise = (async () => {
        try {
          await updateLeagueData();
          // getMatchResults is now redundant for initial load as data is prefetched
          initialized.value = true;
        } finally {
          initPromise = null;
        }
      })();

      return initPromise;
    }

    /**
     * Non-blocking refresh used by `init()` when cached data is already
     * available. Ensures at most one background refresh is in flight at a time.
     */
    function refreshInBackground(): Promise<void> {
      if (refreshPromise) return refreshPromise;
      refreshPromise = (async () => {
        try {
          await updateLeagueData({ background: true });
        } catch {
          // Silently ignore — the stale cached data is still shown to the user.
        } finally {
          refreshPromise = null;
        }
      })();
      return refreshPromise;
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
    const isMeBanningGame = computed(() => {
      const me = members.value.find((m) => isMe(m.username));
      return (
        leagueStatus.value === 'BANNING' &&
        isMeActivePlayer.value &&
        me &&
        !me.has_banned
      );
    });

    return {
      // state
      loading,
      refreshing,
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
      init,
      updateLeagueData,
      refreshInBackground,
      refreshResultsForGame,
      hasSelectedGameResult,
      refresh,
    };
  });
}

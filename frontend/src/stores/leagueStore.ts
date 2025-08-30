// stores/leagueStore.ts
import { defineStore } from 'pinia';
import { ref, computed, shallowRef, watch } from 'vue';
import { getMyLeagueId } from 'src/services/game/leagueService';
import { fetchLeagueDetails } from 'src/services/leagueService';
import { useUserStore } from 'stores/userStore';
import { banGame } from 'src/services/game/banGameService';
import { api } from 'boot/axios';

/**
 * Store for managing and interacting with league-specific data and state.
 * Handles initialization of league data, user actions such as banning games,
 * and computed properties for determining user roles and statuses within the league.
 *
 * State:
 * - `leagueId`: A reference holding the current league's unique identifier.
 * - `leagueData`: A shallow reference containing the broader league data fetched from an API.
 * - `members`: A reference holding the list of members in the current league.
 * - `selectedGames`: A reference containing a list of games selected by members.
 * - `leagueStatus`: A reference to the current status of the league (e.g., "PICKING", "BANNING").
 * - `initialized`: A flag indicating the initialization state of the store.
 *
 * Getters:
 * - `activePlayer`: Computes the currently active player in the league based on member data.
 * - `isMeActivePlayer`: Indicates whether the current user is the active player in the league.
 * - `isMePickingGame`: Checks if the current user is actively picking a game.
 * - `isMeBanningGame`: Checks if the current user is actively banning a game.
 *
 * Actions:
 * - `init`: Initializes the store by fetching the league ID and related data.
 * - `updateLeagueData`: Updates the league's data, members list, and status from an API.
 * - `banNothing`: Allows a user to skip banning a game within the league, if conditions allow.
 *
 * Watchers:
 * - Watches for changes in the `members` list to automatically update the `selectedGames` property.
 */
export const useLeagueStore = defineStore('league', () => {
  // leagueData
  const leagueId = ref<number | null>(null);
  const leagueData = shallowRef<any>(null);
  const members = ref<any[]>([]);
  const selectedGames = ref<any[]>([]);
  const leagueStatus = ref<string>(''); // states: PICKING, BANNING, REPICKING, PLAYING, DONE

  // match results
  const selectedGameIdsWithResults = computed(() =>
    Array.from(
      new Set(matchResults.value.map((result) => result.selected_game))
    ).map((id) => id)
  );

  const selectedGameIdsWithoutResults = computed(() =>
    selectedGames.value
      .map((game) => game.id)
      .filter((id) => !selectedGameIdsWithResults.value.includes(id))
  );

  const selectedGamesWithResults = computed(() =>
    selectedGames.value.filter((game) =>
      selectedGameIdsWithResults.value.includes(game.id)
    )
  );
  const selectedGamesWithoutResults = computed(() =>
    selectedGames.value.filter((game) =>
      selectedGameIdsWithoutResults.value.includes(game.id)
    )
  );

  const matchResults = ref<any[]>([]);

  const initialized = ref(false);
  let initPromise: Promise<void> | null = null;

  async function updateLeagueData() {
    if (leagueId.value == null) return;
    const { data } = await fetchLeagueDetails(leagueId.value);
    leagueData.value = data;
    members.value = data.members;
    leagueStatus.value = data.status;
  }

  async function getMatchResults() {
    if (leagueId.value == null) return;
    const selectedGameIds = selectedGames.value.map((s) => s.id);
    for (const id of selectedGameIds) {
      const { data } = await api.get(`/result/results/?selected_game=${id}`);
      matchResults.value.push(...data);
    }
  }

  function getSelectedGames() {
    if (members.value.length === 0) return [];
    members.value.forEach((member) => {
      selectedGames.value.push({
        ...member.selected_game,
        selected_by: member.username,
      });
    });
  }

  function getUsernameByMemberId(memberId: number) {
    const member = members.value.find((m) => m.id === memberId);
    if (member) return member.username;
    return '';
  }

  function getGameNameBySelectedGameId(selectedGameId: number) {
    const selectedGame = selectedGames.value.find((s) => s.id === selectedGameId);
    if (selectedGame) return selectedGame.game_name;
    return null;
  }

  watch(members, getSelectedGames, { deep: true });

  async function init() {
    // If we've already initialized once, just exit early
    if (initialized.value) return;

    // If another call to init() is already in progress,
    // return the same Promise so we don't start a duplicate request
    if (initPromise) return initPromise;

    // Otherwise, start the initialization process
    // and store the Promise so concurrent callers can reuse it
    initPromise = (async () => {
      // fetch leagueId first
      leagueId.value = await getMyLeagueId();

      // then fetch league details
      await updateLeagueData();
      await getMatchResults();

      // mark as fully initialized
      initialized.value = true;

      // reset the initPromise so future calls don't get stuck on an old Promise
      initPromise = null;
    })();

    // return the Promise so the caller can await initialization
    return initPromise;
  }

  const activePlayer = computed(() =>
    members.value.find((m) => m.is_active_player)
  );

  const { isMe, user } = useUserStore();
  const isMeActivePlayer = computed(() =>
    activePlayer.value ? isMe(activePlayer.value.username) : false
  );

  const isMePickingGame = computed(
    () => leagueStatus.value === 'PICKING' && isMeActivePlayer.value
  );
  const isMeBanningGame = computed(
    () => leagueStatus.value === 'BANNING' && isMeActivePlayer.value
  );

  async function banNothing() {
    if (!user || !leagueId.value) return;
    await banGame({ username: user.username, leagueId: leagueId.value });
  }

  return {
    // state
    leagueId, leagueData, members, leagueStatus, initialized, selectedGames, matchResults,
    // getters
    activePlayer, isMeActivePlayer, isMePickingGame, isMeBanningGame, selectedGamesWithResults, selectedGamesWithoutResults, selectedGameIdsWithResults, selectedGameIdsWithoutResults,
    // actions
    init, updateLeagueData, banNothing, getUsernameByMemberId, getGameNameBySelectedGameId
  };
});

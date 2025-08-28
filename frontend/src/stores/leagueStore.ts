// stores/leagueStore.ts
import { defineStore } from 'pinia';
import { ref, computed, shallowRef, watch } from 'vue';
import { getMyLeagueId } from 'src/services/game/leagueService';
import { fetchLeagueDetails } from 'src/services/leagueService';
import { useUserStore } from 'stores/userStore';
import { banGame } from 'src/services/game/banGameService';

export const useLeagueStore = defineStore('league', () => {
  const leagueId = ref<number | null>(null);
  const leagueData = shallowRef<any>(null);
  const members = ref<any[]>([]);
  const selectedGames = ref<any[]>([]);
  const leagueStatus = ref<string>('');
  const initialized = ref(false);
  let initPromise: Promise<void> | null = null;

  async function updateLeagueData() {
    if (leagueId.value == null) return;
    const { data } = await fetchLeagueDetails(leagueId.value);
    leagueData.value = data;
    members.value = data.members;
    leagueStatus.value = data.status;
  }

  function getSelectedGames() {
    if(members.value.length === 0) return [];
    members.value.forEach(member => {
      selectedGames.value.push({ ...member.selected_game, selected_by: member.username })
    })
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
    leagueId, leagueData, members, leagueStatus, initialized, selectedGames,
    // getters
    activePlayer, isMeActivePlayer, isMePickingGame, isMeBanningGame,
    // actions
    init, updateLeagueData, banNothing
  };
});

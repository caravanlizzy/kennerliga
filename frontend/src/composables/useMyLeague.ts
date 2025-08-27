import { computed, onMounted, ref } from 'vue';
import { getMyLeagueId } from 'src/services/game/leagueService';
import { fetchLeagueDetails } from 'src/services/leagueService';
import { useUserStore } from 'stores/userStore';
import { banGame } from 'src/services/game/banGameService';

export function useMyLeague() {
  let leagueId = ref();
  let hasComposableBeenMounted = false;

  const { isMe, user } = useUserStore();

  const leagueData = ref<any>(null);
  const members = ref<any[]>([]);
  const leagueStatus = ref<string>('');

  async function updateLeagueData() {
    const { data } = await fetchLeagueDetails(leagueId.value);
    leagueData.value = data;
    members.value = data.members;
    leagueStatus.value = data.status;
  }

  onMounted(async () => {
    if (hasComposableBeenMounted) return;
    leagueId.value = await getMyLeagueId()
    await updateLeagueData();
    hasComposableBeenMounted = true;
  })
  // computed properties
  const activePlayer = computed(() =>
    members.value.find((member) => member.is_active_player)
  );

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
    if (!user || !leagueId) return;
    try {
      await banGame({
        username: user.username,
        leagueId: leagueId.value,
      });
    } catch (error) {
      console.error('Failed to ban nothing:', error);
    }
  }

  return {
    state: { leagueData, leagueId, members, leagueStatus, activePlayer, isMePickingGame, isMeBanningGame },
    actions: { updateLeagueData, banNothing }
  };
}

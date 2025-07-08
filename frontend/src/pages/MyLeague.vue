<template>
  <div class="q-pa-lg">
    <LeagueStatusBar
      :league="league"
      :status="status"
      :activePlayer="activePlayer"
      :isPlayerBanning="isPlayerBanning"
    />

    <!-- Game Selector -->
    <GameSelector
      v-if="isPlayerPicking"
      @submit-success="fetchLeagueDetails"
      class="q-mt-xl"
      :leagueId="myLeagueId"
    />

    <GameResult v-if="status === 'PLAYING'" :league="league" />

    <!-- Player Cards Grid -->
    <PlayerCardList
      :members="members"
      :status="status"
      :activePlayer="activePlayer?.username"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, provide, ref } from 'vue';
import { api } from 'boot/axios';
import GameSelector from 'components/league/GameSelector.vue';
import { useUserStore } from 'stores/userStore';
import PlayerCardList from 'components/league/PlayerCardList.vue';
import { getMyLeagueId } from 'src/services/game/leagueService';
import { banGame } from 'src/services/game/banGameService';
import GameResult from 'components/league/GameResult.vue';
import LeagueStatusBar from 'pages/LeagueStatusBar.vue';

const league = ref<any>(null);
const members = ref<any[]>([]);
const status = ref<string>('');
const myLeagueId = ref<number | null>(null);
const { isMe, user } = useUserStore();

const fetchLeagueDetails = async () => {
  const { data } = await api.get(`league/league-details/${myLeagueId.value}`);
  league.value = data;
  members.value = data.members;
  status.value = data.status;
};

onMounted(async () => {
  try {
    myLeagueId.value = await getMyLeagueId();
    await fetchLeagueDetails();
  } catch (err) {
    console.error('Error loading league details:', err);
  }
});

const activePlayer = computed(() =>
  members.value.find((member) => member.is_active_player)
);

const isPlayerActive = computed(() =>
  activePlayer.value ? isMe(activePlayer.value.username) : false
);

const isPlayerPicking = computed(
  () => league.value?.status === 'PICKING' && isPlayerActive.value
);

const isPlayerBanning = computed(
  () => league.value?.status === 'BANNING' && isPlayerActive.value
);

function banNothin() {
  banGame({
    username: user?.username,
    leagueId: myLeagueId.value,
  });
}

provide('league', league);
provide('fetchLeagueDetails', fetchLeagueDetails);
</script>

<style lang="scss">
.player-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 0;
}

.column-reverse {
  display: flex;
  flex-direction: column-reverse;
  gap: 16px;
}

.is-active-border-accent {
  border: 2px solid rgba($accent, 0.4);
}

.is-active-border-secondary {
  border: 2px solid rgba($secondary, 0.4);
}

.league-card {
  background: #f3f3f3;
  border-radius: 8px;
  margin: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}
</style>

<template>
  <div class="q-pa-lg">
    <!-- Status Bar -->
    <div
      class="q-pa-lg column justify-center items-center text-primary border border-primary rounded-borders"
    >

      <div class="text-h6 text-uppercase text-weight-bold q-mb-sm">
        {{ statusNoun }}
      </div>

      <div class="text-subtitle1 text-center">
        <span class="text-primary text-weight-bold">
          {{ activePlayer?.username }}
        </span>
        <span
          v-if="status === 'PICKING' || status === 'BANNING'"
          class="q-mx-xs"
          >muss ein Spiel
        </span>
        <span
          class="text-weight-bold"
          :class="{
            'text-accent': league?.status === 'BANNING',
            'text-secondary': league?.status === 'PICKING',
          }"
        >
          {{ statusVerb }}
        </span>
      </div>
      <q-btn
        v-if="isPlayerBanning"
        color="accent"
        outline
        class="q-mt-sm"
        @click="banNothin"
      >
        Banne nichts
      </q-btn>
    </div>

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
import ResultMatchForm from 'components/league/ResultMatchForm.vue';
import SelectedGameResult from 'components/league/SelectedGameResult.vue';
import GameResult from 'components/league/GameResult.vue';

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

const isPlayerBanning = computed(
  () => league.value?.status === 'BANNING' && isPlayerActive.value
);

const isPlayerPicking = computed(
  () => league.value?.status === 'PICKING' && isPlayerActive.value
);

type LeagueStatus = 'PICKING' | 'BANNING' | 'PLAYING' | 'DONE' | string;

const statusMap: Record<LeagueStatus, { noun?: string; verb?: string }> = {
  PICKING: { noun: 'Spielauswahl', verb: 'auswählen' },
  BANNING: { noun: 'Bannen', verb: 'bannen' },
  PLAYING: { noun: 'Spiele laufen' },
  DONE: { noun: 'Beendet' },
};

const statusNoun = computed(
  () => statusMap[league.value?.status as LeagueStatus]?.noun ?? ''
);

const statusVerb = computed(
  () => statusMap[league.value?.status as LeagueStatus]?.verb ?? ''
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

<style lang="scss" scoped>
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

.player-card {
  /* Optional: visual grouping for each card */
  border: 1px solid #e0e0e0;
  border-radius: 2px;
  padding: 12px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04);
  transition: box-shadow 0.3s ease;
  background: white;
}

.is-active-border-accent {
  border: 2px solid rgba($accent, 0.4);
}

.is-active-border-secondary {
  border: 2px solid rgba($secondary, 0.4);
}

.player-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}
</style>

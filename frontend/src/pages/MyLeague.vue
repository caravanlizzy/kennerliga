<template>
  <div class="q-pa-lg">
    <!-- Status Bar -->
    <div
      class="q-pa-lg column justify-center items-center text-primary border border-primary rounded-borders"
    >
      <div class="text-h6 text-uppercase text-weight-bold q-mb-sm">
        {{ statusNoun }} {{  }}
      </div>

      <div class="text-subtitle1 text-center">
        <span class="text-accent text-weight-bold">
          {{ activePlayer?.username }}
        </span>
        <span class="q-mx-xs">muss ein Spiel</span>
        <span class="text-accent text-weight-bold">
          {{ statusVerb }}
        </span>
      </div>
    </div>

    <!-- Game Selector -->
    <GameSelector v-if="isActive && league.status === 'PICKING'" @submit-success="fetchLeagueDetails" class="q-mt-xl"/>
    <div class="q-pa-lg" v-if="isActive && league.status ==='BANNING'">
      <q-btn
        size="lg"
        :color="selectedGame === selectedBan ? 'accent' : undefined"
        class="q-mx-md"
        @click="() => selectedBan = selectedGame"
        v-for="selectedGame of selectedGames" :key="selectedGame">
        {{ selectedGame}}
      </q-btn>
    </div>

    <!-- Player Cards -->
    <div
      style="display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; height: 100%; gap: 0;"
    >
      <div
        v-for="(member, index) in members"
        :key="member.id"
        :class="getQuadrantBorder(index)"
      >
        <LeagueUserCard :statusVerb="statusVerb" :member="member" :isActive="member.is_active_player"/>
      </div>
    </div>

  </div>
</template>


<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { api } from 'boot/axios';
import GameSelector from 'components/ui/GameSelector.vue';
import { useUserStore } from 'stores/userStore';
import LeagueUserCard from 'components/cards/LeagueUserCard.vue';

/**
 * Returns border classes to simulate a cross layout.
 * Index 0 = top-left, 1 = top-right, 2 = bottom-left, 3 = bottom-right
 */
const getQuadrantBorder = (index: number) => {
  switch (index) {
    case 0:
      return `border-right border-bottom`;
    case 1:
      return `border-left border-bottom`;
    case 2:
      return `border-right border-top`;
    case 3:
      return `border-left border-top`;
    default:
      return '';
  }
};

const league = ref<any>(null);
const members = ref<any[]>([]);
const selectedGames = computed(() => league.value?.members.map((member) => member.selected_game));
const selectedBan = ref<any>(null);
const { isMe } = useUserStore();

const myleagueId = 1;

const fetchLeagueDetails = async () => {
  const { data } = await api.get(`league/league-details/${myleagueId}`);
  league.value = data;
  members.value = data.members;
};

onMounted(async () => {
  try {
    await fetchLeagueDetails();
  } catch (err) {
    console.error('Error loading league details:', err);
  }
});

const activePlayer = computed(() =>
  members.value.find((member) => member.id === league.value?.active_player)
);

const isActive = computed(() =>
  activePlayer.value ? isMe(activePlayer.value.username) : false
);

type LeagueStatus = 'PICKING' | 'BANNING' | 'PLAYING' | 'DONE' | string;

const statusMap: Record<LeagueStatus, { noun?: string; verb?: string }> = {
  PICKING: { noun: 'Spielauswahl', verb: 'auswählen' },
  BANNING: { noun: 'Bannen', verb: 'bannen' },
  PLAYING: { noun: 'Spiele laufen' },
  DONE: { noun: 'Beendet' },
};

const statusNoun = computed(() =>
  statusMap[league.value?.status as LeagueStatus]?.noun ?? ''
);

const statusVerb = computed(() =>
  statusMap[league.value?.status as LeagueStatus]?.verb ?? ''
);

</script>

<style scoped>
.gradient {
  background: linear-gradient(to bottom, #fafafa, #f0f0f0);
}

.border-top {
  border-top: 1px solid #ccc;
}

.border-right {
  border-right: 1px solid #ccc;
}

.border-bottom {
  border-bottom: 1px solid #ccc;
}

.border-left {
  border-left: 1px solid #ccc;
}

</style>

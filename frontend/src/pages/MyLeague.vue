<template>
  <div class="q-pa-lg">
    <!-- Status Bar -->
    <div
      class="q-pa-xl column justify-center items-center bg-grey-2 text-primary border border-primary rounded-borders"
    >
      <!-- Phase Label -->
      <div class="text-h6 text-uppercase text-weight-bold q-mb-sm">
        {{ statusNoun }}
      </div>

      <!-- Player Action Prompt -->
      <div class="text-subtitle1 text-center">
        <span class="text-accent text-weight-bold">{{ activePlayer?.username }}</span>
        <span class="q-mx-xs">muss ein Spiel</span>
        <span class="text-accent text-weight-bold">{{ statusVerb }}</span>
      </div>
    </div>

    <!-- Main Content -->
    <div class="gradient">
<!--      <KennerButton @click="next">Next</KennerButton>-->

      <!-- Player Boxes -->
      <div class="row q-gutter-md q-mt-md">
        <div
          v-for="member in members"
          :key="member.id"
          class="q-pa-md q-mb-sm col-12 col-sm-6 col-md-4 border rounded-borders"
          :class="member.id === activePlayer?.id ? 'bg-primary text-white' : 'bg-grey-2 text-dark'"
        >
          <div class="text-subtitle2 text-weight-medium">
            {{ member.username }}
          </div>

          <div class="q-mt-sm row items-center q-gutter-sm">
            <q-chip
              v-if="member"
              label="Ausgewählt"
              color="secondary"
              text-color="white"
              dense
              icon="check"
            />
            <q-chip
              v-if="member"
              label="Gebannt"
              color="negative"
              text-color="white"
              dense
              icon="block"
            />
          </div>

          <div v-if="member.selectedGame" class="q-mt-sm text-caption">
            Spiel: <span class="text-weight-bold">{{ member.selectedGame }}</span>
          </div>
        </div>
      </div>
    </div>

    <GameSelector v-if="isActive" class="q-mt-lg" />
  </div>
</template>

<script setup lang="ts">
import GameSelector from 'components/ui/GameSelector.vue';
import { computed, onMounted, ref } from 'vue';
import KennerButton from 'components/buttons/KennerButton.vue';
import { api } from 'boot/axios';

const league = ref();
const members = ref([]);
const activePlayer = computed(() =>
  members.value.find((member) => member.id === league.value.active_player)
);

type LeagueStatus = 'PICKING' | 'BANNING' | 'PLAYING' | 'DONE' | string;

const statusMap: Record<LeagueStatus, { noun?: string; verb?: string }> = {
  PICKING: { noun: 'Spielauswahl', verb: 'auswählen' },
  BANNING: { noun: 'Bannen', verb: 'bannen' },
  PLAYING: { noun: 'Spiele laufen' },
  DONE: { noun: 'Beendet' },
};

const statusNoun = computed(() => {
  return statusMap[league.value?.status as LeagueStatus]?.noun ?? '';
});

const statusVerb = computed(() => {
  return statusMap[league.value?.status as LeagueStatus]?.verb ?? '';
});

const myleagueId = 1;

onMounted(async () => {
  try {
    const data = await fetchLeague();
    await fetchLeagueMembers(data);
  } catch (err) {
    console.error('Error loading league/members:', err);
  }
});

async function fetchLeague() {
  const { data } = await api.get(`league/leagues/${myleagueId}`);
  league.value = data;
  return data; // allows optional chaining
}

async function fetchLeagueMembers(leagueData: any) {
  const memberData = await Promise.all(
    leagueData.members.map(async (memberId: number) => {
      const { data } = await api.get(`user/users/${memberId}/`);
      return data;
    })
  );
  members.value = memberData;
  return memberData;
}

function next() {
  api({
    url: '/league/1/next-player/',
    method: 'POST',
  }).then(() => {
    fetchLeague();
  });
}

const isActive = ref(true);
</script>

<template>
  <div class="q-pa-sm">
    <q-card class="league-card q-pa-md">
      <!-- Header with toggler -->
      <div class="row items-center justify-between q-mb-sm">
        <div class="text-h6">Ergebnis eintragen</div>
        <q-btn
          flat
          round
          dense
          size="sm"
          icon="expand_more"
          class="toggle-btn"
          :class="{ rotated: showForm }"
          @click="showForm = !showForm"
        />
      </div>

      <!-- Tabs on top -->
      <div class="tab-wrapper q-mb-sm">
        <q-tabs
          v-model="selectedGameId"
          :vertical="!isDesktop"
          active-color="primary"
          indicator-color="primary"
          align="left"
          narrow-indicator
          class="text-primary"
          swipeable
        >
          <q-tab
            v-for="game in uniqueSelectedGames"
            :key="game.id"
            :name="game.id"
            :label="game.game_name"
          />
        </q-tabs>
      </div>

      <!-- Form or Result -->
      <div v-show="showForm">
        <q-separator class="q-mb-sm" />
        <keep-alive include="ResultMatchForm">
          <component
            :is="hasResult(selectedGameId) ? MatchResult : ResultMatchForm"
            v-if="selectedGameId"
            :key="selectedGameId"
            :selected-game-id="selectedGameId"
            :players="getPlayersForGame(selectedGameId)"
            v-bind="hasResult(selectedGameId) ? getResultProps(selectedGameId) : {}"
          />
        </keep-alive>
      </div>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watchEffect, watch } from 'vue';
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';
import ResultMatchForm from './ResultMatchForm.vue';
import MatchResult from './MatchResult.vue';

const props = defineProps<{
  league: any;
}>();

const $q = useQuasar();
const showForm = ref(true);
const selectedGameId = ref<number | null>(null);
const resultsByGame = ref<Record<number, any[]>>({});

const isDesktop = computed(() => $q.screen.gt.sm);

const allMembers = computed(() => props.league?.members || []);

const uniqueSelectedGames = computed(() => {
  const seen = new Set();
  return allMembers.value
    .map((member) => member.selected_game)
    .filter((game) => game && !seen.has(game.id) && seen.add(game.id));
});

watchEffect(() => {
  if (selectedGameId.value === null && uniqueSelectedGames.value.length > 0) {
    selectedGameId.value = uniqueSelectedGames.value[0].id;
  }
});

watch(selectedGameId, async (id) => {
  showForm.value = true;
  if (id && !resultsByGame.value[id]) {
    try {
      const { data } = await api.get(`/result/results/?selected_game=${id}`);
      resultsByGame.value[id] = data;
    } catch (err) {
      console.error('Fehler beim Laden der Ergebnisse:', err);
      resultsByGame.value[id] = [];
    }
  }
});

function hasResult(selectedGameId: number) {
  console.log('running');
  const results = resultsByGame.value[selectedGameId];
  const totalPlayers = allMembers.value.length;
  return results?.length === totalPlayers;
}

function getPlayersForGame(selectedGameId: number) {
  return allMembers.value.map((member) => ({
    id: member.id,
    username: member.username,
  }));
}

function getResultProps(selectedGameId: number) {
  const game = uniqueSelectedGames.value.find(g => g.id === selectedGameId);
  const results = resultsByGame.value[selectedGameId] || [];

  const enriched = allMembers.value.map(member => {
    const result = results.find(r => r.player_profile === member.id);
    return {
      id: member.id,
      username: member.username,
      ...result,
    };
  });

  return {
    gameName: game?.game_name || 'Spiel',
    results: enriched,
  };
}
</script>

<style scoped>
.toggle-btn {
  transition: transform 0.2s ease;
}

.toggle-btn.rotated {
  transform: rotate(180deg);
}
</style>

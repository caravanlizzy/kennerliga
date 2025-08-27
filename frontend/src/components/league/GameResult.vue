<template>
  <div>
    <q-card flat class="league-card q-pa-md">
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
import { ref, computed, watch } from 'vue';
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';
import ResultMatchForm from './ResultMatchForm.vue';
import MatchResult from './MatchResult.vue';
import { storeToRefs } from 'pinia';
import { useLeagueStore } from 'stores/leagueStore';

const {  members } = storeToRefs(useLeagueStore());

const $q = useQuasar();
const showForm = ref(false);
const selectedGameId = ref<number | null>(null);
const resultsByGame = ref<Record<number, any[]>>({});

const isDesktop = computed(() => $q.screen.gt.sm);

const uniqueSelectedGames = computed(() => {
  const seen = new Set();
  return members.value
    .map((member) => member.selected_game)
    .filter((game) => game && !seen.has(game.id) && seen.add(game.id));
});

// Replace the two watchers with this single one
watch(
  [selectedGameId, uniqueSelectedGames],
  async ([newSelectedGameId, games]) => {
    // Auto-select the first game if none selected yet
    if (newSelectedGameId === null && games.length > 0) {
      selectedGameId.value = games[0].id;
      return; // wait for next tick where selectedGameId is set to fetch
    }

    // With a valid selection, show the form and fetch results if needed
    if (newSelectedGameId != null) {
      showForm.value = true;

      if (!resultsByGame.value[newSelectedGameId]) {
        try {
          const { data } = await api.get(
            `/result/results/?selected_game=${newSelectedGameId}`
          );
          resultsByGame.value[newSelectedGameId] = data;
        } catch (err) {
          console.error('Fehler beim Laden der Ergebnisse:', err);
          resultsByGame.value[newSelectedGameId] = [];
        }
      }
    }
  },
  { immediate: true }
);

function hasResult(selectedGameId: number) {
  const results = resultsByGame.value[selectedGameId];
  return results?.length === members.value.length;
}

function getPlayersForGame(selectedGameId: number) {
  return members.value.map((member) => ({
    id: member.id,
    username: member.username,
    position: member.position,
  }));
}

function getResultProps(selectedGameId: number) {
  const game = uniqueSelectedGames.value.find(g => g.id === selectedGameId);
  const results = resultsByGame.value[selectedGameId] || [];

  const enriched = members.value.map(member => {
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

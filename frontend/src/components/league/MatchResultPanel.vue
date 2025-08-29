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
            v-for="game in selectedGames"
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
                :is="hasResultForSelected ? 'MatchResult' : 'MatchResultForm'"
                v-if="selectedGameId"
                :key="selectedGameId"
                :selected-game-id="selectedGameId"
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
import MatchResultForm from './MatchResultForm.vue';
import MatchResult from './MatchResult.vue';
import { storeToRefs } from 'pinia';
import { useLeagueStore } from 'stores/leagueStore';

const { members, selectedGames, matchResults } = storeToRefs(useLeagueStore());

const $q = useQuasar();
const showForm = ref(false);
const selectedGameId = ref<number | null>(null);

// reactive boolean for the currently selected game
const hasResultForSelected = computed(() => {
  const id = selectedGameId.value;
  if (!id) return false;
  const results = matchResults.value[id] ?? [];
  return results.length === members.value.length;
});

const isDesktop = computed(() => $q.screen.gt.sm);


// // Replace the two watchers with this single one
// watch(
//   [selectedGameId, selectedGames],
//   async ([newSelectedGameId, games]) => {
//     // Auto-select the first game if none selected yet
//     if (newSelectedGameId === null && games.length > 0) {
//       selectedGameId.value = games[0].id;
//       return; // wait for next tick where selectedGameId is set to fetch
//     }
//
//     // With a valid selection, show the form and fetch results if needed
//     if (newSelectedGameId != null) {
//       showForm.value = true;
//
//       if (!matchResults.value[newSelectedGameId]) {
//         try {
//           await api.get(
//             `/result/results/?selected_game=${newSelectedGameId}`
//           );
//           matchResults.value[newSelectedGameId] = data;
//         } catch (err) {
//           console.error('Fehler beim Laden der Ergebnisse:', err);
//           matchResults.value[newSelectedGameId] = [];
//         }
//       }
//     }
//   },
//   { immediate: true }
// );

</script>

<style scoped>
.toggle-btn {
  transition: transform 0.2s ease;
}

.toggle-btn.rotated {
  transform: rotate(180deg);
}
</style>

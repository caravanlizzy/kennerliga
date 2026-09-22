<template>
  <div v-if="selectedGamesFetchedEmpty.length > 0" class="column q-gutter-y-md">
    <div class="text-caption text-grey-7">
      Select a game below to record final scores and rankings:
    </div>

    <div class="row q-gutter-sm items-center">
      <KennerButton
        v-for="selectedGame in selectedGamesFetchedEmpty"
        :key="selectedGame.id"
        :label="selectedGame.game_name"
        :color="currentFormSelectedGameId === selectedGame.id ? 'primary' : 'grey-3'"
        :text-color="currentFormSelectedGameId === selectedGame.id ? 'white' : 'dark'"
        :unelevated="currentFormSelectedGameId === selectedGame.id"
        :flat="currentFormSelectedGameId !== selectedGame.id"
        icon="sports_esports"
        no-caps
        class="game-tab-btn"
        @click="currentFormSelectedGameId = selectedGame.id"
      />
    </div>

    <!-- Match Result Entry Form -->
    <MatchResultForm
      v-if="currentFormSelectedGameId && leagueData"
      :selected-game-id="currentFormSelectedGameId"
      :league-id="leagueData.id"
      :league="leagueData"
      @submitted="handleSubmit"
    />
    <div v-else class="text-center q-pa-md text-grey-6 italic">
      Click a game button above to enter match results.
    </div>
  </div>
  <div v-else class="text-center q-pa-md text-grey-7">
    <q-icon name="check_circle" size="32px" color="positive" class="q-mb-xs" />
    <div class="text-subtitle2 text-weight-bold">All matches have been reported!</div>
    <div class="text-caption text-grey-6 q-mt-xs">
      All results for this league are submitted and reflected in the standings above.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { storeToRefs } from 'pinia';
import MatchResultForm from 'components/league/MatchResultForm.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { useMyLeagueStore } from 'src/composables/myLeague';

const myLeagueStore = useMyLeagueStore();
const { selectedGamesFetchedEmpty, leagueData } = storeToRefs(myLeagueStore);
const { refreshResultsForGame } = myLeagueStore;

const currentFormSelectedGameId = ref<number | null>(null);

watch(
  selectedGamesFetchedEmpty,
  (emptyGames) => {
    if (emptyGames.length > 0) {
      if (!currentFormSelectedGameId.value || !emptyGames.some((g) => g.id === currentFormSelectedGameId.value)) {
        currentFormSelectedGameId.value = emptyGames[0]?.id ?? null;
      }
    } else {
      currentFormSelectedGameId.value = null;
    }
  },
  { immediate: true }
);

function handleSubmit(selectedGameId: number) {
  currentFormSelectedGameId.value = null;
  void refreshResultsForGame(selectedGameId);
}
</script>

<style scoped lang="scss">
.game-tab-btn {
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 10px;
  font-weight: 600;
  transition: all 0.2s ease;
}
</style>

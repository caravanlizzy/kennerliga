<template>
  <!-- Game Tabs for Entering Results -->
  <q-tabs
    v-model="currentFormSelectedGameId"
    active-color="primary"
    indicator-color="primary"
    :vertical="isMobile"
  >
    <q-tab
      v-for="selectedGame in selectedGamesFetchedEmpty"
      :key="selectedGame.id"
      :name="selectedGame.id"
    >
      {{ truncateString(selectedGame.game_name) }}
    </q-tab>
  </q-tabs>

  <!-- Match Result Entry Form -->
  <MatchResultForm
    v-if="currentFormSelectedGameId"
    @submitted="handleSubmit"
    :selected-game-id="currentFormSelectedGameId"
  />
</template>

<script setup lang="ts">
import MatchResultForm from 'components/league/MatchResultForm.vue';
import { storeToRefs } from 'pinia';
import { useLeagueStore } from 'stores/leagueStore';
import { ref } from 'vue';
import { useResponsive } from 'src/composables/reponsive';
import { truncateString } from 'src/helpers';
const { selectedGamesFetchedEmpty } = storeToRefs(useLeagueStore());
const { refreshResultsForGame } = useLeagueStore();
const { isMobile } = useResponsive();

const currentFormSelectedGameId = ref(null);

function handleSubmit(selectedGameId: number) {
  currentFormSelectedGameId.value = null;
  refreshResultsForGame(selectedGameId);
}
</script>

<style scoped></style>

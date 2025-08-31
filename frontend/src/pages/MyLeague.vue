<template>
  <div>
    <LeagueStatusBar />

    <!-- Game Selector - shown when user needs to pick games -->
    <GameSelector
      v-if="isMePickingGame"
      @submit-success="updateLeagueData"
      class="q-mt-xl"
    />

    <!-- Match Results Section -->
    <template v-if="leagueStatus === 'PLAYING'">
      <!-- Game Tabs for Entering Results -->
      <q-tabs
        active-color="primary"
        indicator-color="primary"
        v-model="currentFormSelectedGameId"
      >
        <q-tab
          v-for="selectedGame in selectedGamesFetchedEmpty"
          :key="selectedGame.id"
          :name="selectedGame.id"
        >
          {{ selectedGame.game_name }}
        </q-tab>
      </q-tabs>
      <!-- Match Result Entry Form -->
      <MatchResultForm
        v-if="currentFormSelectedGameId"
        @submitted="handleSubmit"
        :selected-game-id="currentFormSelectedGameId"
      />

      <q-separator />

      <!-- Display Previously Entered Match Results -->
      <div class="flex">
        <MatchResult
          v-for="selectedGame of selectedGamesWithResults"
          :key="selectedGame.id"
          :selected-game-id="selectedGame.id"
        />
      </div>
    </template>

    <!-- Player Cards Grid -->
    <PlayerCardList />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import GameSelector from 'components/league/GameSelector.vue';
import PlayerCardList from 'components/league/PlayerCardList.vue';
import LeagueStatusBar from 'pages/LeagueStatusBar.vue';
import { useLeagueStore } from 'stores/leagueStore';
import { storeToRefs } from 'pinia';
import MatchResult from 'components/league/MatchResult.vue';
import MatchResultForm from 'components/league/MatchResultForm.vue';

const league = useLeagueStore();

onMounted(() => {
  void league.init();
});

const {
  isMePickingGame,
  leagueStatus,
  selectedGamesFetchedEmpty,
  selectedGamesWithResults,
} = storeToRefs(league);
const { updateLeagueData, refreshResultsForGame } = league;

const currentFormSelectedGameId = ref(null);

function handleSubmit(selectedGameId: number) {
  currentFormSelectedGameId.value = null;
  refreshResultsForGame(selectedGameId);
}
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
  //background: #f3f3f3;
  border-radius: 8px;
  margin: 8px;
  overflow: hidden;
  //box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}
</style>

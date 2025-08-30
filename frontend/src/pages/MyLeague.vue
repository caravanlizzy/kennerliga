<template>
  <div class="q-pa-lg">
    <LeagueStatusBar />

    <!-- Game Selector -->
    <GameSelector
      v-if="isMePickingGame"
      @submit-success="updateLeagueData"
      class="q-mt-xl"
    />

    <template v-if="leagueStatus === 'PLAYING'">
      <div class="flex">
        <MatchResult
          v-for="selectedGameId of selectedGameIdsWithResults"
          :key="selectedGameId"
          :selected-game-id="selectedGameId"
        />
      </div>
      <q-separator />
      <q-tabs
        active-color="primary"
        indicator-color="primary"
        v-model="currentFormSelectedGameId"
      >
        <q-tab
          v-for="selectedGame in selectedGamesWithoutResults"
          :key="selectedGame.id"
          :name="selectedGame.id"
        >
          {{ selectedGame.game_name }}
        </q-tab>
      </q-tabs>
      <MatchResultForm
        v-if="currentFormSelectedGameId"
        :selected-game-id="currentFormSelectedGameId"
      />
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
  selectedGamesWithResults,
  selectedGameIdsWithResults,
  selectedGameIdsWithoutResults,
  selectedGamesWithoutResults,
} = storeToRefs(league);
const { updateLeagueData } = league;

const currentFormSelectedGameId = ref(null);
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

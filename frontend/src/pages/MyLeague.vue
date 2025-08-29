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
      <MatchResult
        v-for="selectedGameId of selectedGamesWithResults"
        :key="selectedGameId"
        :selected-game-id="selectedGameId"
      />
      <q-separator/>
      <MatchResultForm
        v-for="selectedGameId of selectedGamesWithoutResults"
        :key="selectedGameId"
        :selected-game-id="selectedGameId"
      />
    </template>

    <!-- Player Cards Grid -->
    <PlayerCardList />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
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
})

const { isMePickingGame, leagueStatus, selectedGamesWithResults, selectedGamesWithoutResults } = storeToRefs(league);
const { updateLeagueData } = league;

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

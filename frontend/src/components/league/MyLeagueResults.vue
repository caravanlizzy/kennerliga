<template>
  <div class="row no-wrap">
    <!-- Match results -->
    <div class="row">
      <MatchResult
        v-for="selectedGame of selectedGamesWithResults"
        :key="selectedGame.id"
        :selected-game-id="selectedGame.id"
      />
    </div>

    <!-- League standings -->
    <LeagueStandings class="q-ml-auto" />
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';

const { selectedGamesWithResults } = storeToRefs(useLeagueStore());

import MatchResult from 'components/league/MatchResult.vue';
import LeagueStandings from 'components/league/LeagueStandings.vue';
import { useLeagueStore } from 'stores/leagueStore';
</script>

<style scoped>
.border-right {
  border-right: 1px solid #ddd;
  margin: 2px;
}
</style>

<template>
  <div class="q-pa-xs">
    <!-- Match results -->
    <div class="row justify-center">

      <MatchResult
        v-for="selectedGame of selectedGamesWithResults"
        :key="selectedGame.id"
        :selected-game-id="selectedGame.id"
      />
    </div>

    <!-- League standings -->
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';

const { selectedGamesWithResults } = storeToRefs(useLeagueStore());

import MatchResult from 'components/league/MatchResult.vue';
import LeagueStandings from 'components/league/LeagueStandings.vue';
import { useLeagueStore } from 'stores/leagueStore';
</script>


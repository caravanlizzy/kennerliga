<template>
  <div>
    <LeagueStatusBar />
    <!-- Game Selector - shown when user needs to pick games -->
    <GameSelector
      v-if="isMePickingGame"
      @submit-success="updateLeagueData"
      class="q-mt-xl"
    />
    <SectionTitle class="bg-primary text-white">Upload Result</SectionTitle>
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

      <!--      <q-separator />-->
      <SectionTitle class="bg-secondary text-white">Results</SectionTitle>
      <MyLeagueResults />
    </template>

    <!-- Player Cards Grid -->

    <SectionTitle class="bg-info text-white">Selected Games</SectionTitle>
    <div class="row wrap justify-between q-pa-md">
      <div v-for="member in members" :key="member.id" class="player-card">
        <PlayerCard :member="member" />
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import GameSelector from 'components/league/GameSelector.vue';
import LeagueStatusBar from 'pages/LeagueStatusBar.vue';
import { useLeagueStore } from 'stores/leagueStore';
import { storeToRefs } from 'pinia';
import MatchResultForm from 'components/league/MatchResultForm.vue';
import PlayerCard from 'components/league/PlayerCard.vue';
import MyLeagueResults from 'components/league/MyLeagueResults.vue';
import SectionTitle from 'components/base/SectionTitle.vue';

const league = useLeagueStore();

onMounted(() => {
  void league.init();
});

const { isMePickingGame, leagueStatus, selectedGamesFetchedEmpty, members } =
  storeToRefs(league);
const { updateLeagueData, refreshResultsForGame } = league;

const currentFormSelectedGameId = ref(null);

function handleSubmit(selectedGameId: number) {
  currentFormSelectedGameId.value = null;
  refreshResultsForGame(selectedGameId);
}
</script>

<style lang="scss">
.is-active-border-accent {
  border: 2px solid rgba($accent, 0.4);
}

.is-active-border-secondary {
  border: 2px solid rgba($secondary, 0.4);
}
</style>

<template>
  <ContentSection
    v-if="leagueStatus === 'PLAYING' || leagueStatus === 'DONE'"
    title="Results"
    color="warning"
    icon="emoji_events"
    v-model:is-opened="isOpened"
    expandable
    bordered
    class="league-section"
  >
    <div
      v-if="selectedGamesWithResults.length > 0"
      class="row q-col-gutter-md"
    >
      <div
        v-for="game in selectedGamesWithResults"
        :key="game.id"
        class="col-12"
        :class="{ 'col-md-6': selectedGamesWithResults.length > 1 }"
      >
        <q-card class="result-card" flat>
          <q-card-section class="q-pa-sm">
            <MatchResult :selectedGame="game" display-game-name />
          </q-card-section>
        </q-card>
      </div>
    </div>
    <div v-else class="text-center q-pa-md text-grey">
      <div class="text-subtitle1">No results recorded yet</div>
      <div v-if="leagueStatus === 'PLAYING'" class="text-caption">
        Games that are finished can be reported below.
      </div>
    </div>
  </ContentSection>
</template>

<script setup lang="ts">
import { ref, watchEffect } from 'vue';
import { storeToRefs } from 'pinia';
import ContentSection from 'components/base/ContentSection.vue';
import MatchResult from 'components/league/MatchResult.vue';
import { useMyLeagueStore } from 'src/composables/myLeague';

const { leagueStatus, selectedGamesWithResults } = storeToRefs(useMyLeagueStore());

const isOpened = ref(false);

watchEffect(() => {
  isOpened.value =
    ['PLAYING', 'DONE'].includes(leagueStatus.value) &&
    selectedGamesWithResults.value.length > 0;
});
</script>

<style scoped>
.league-section {
  margin-bottom: 16px;
}

.result-card {
  border-radius: 10px;
}
</style>

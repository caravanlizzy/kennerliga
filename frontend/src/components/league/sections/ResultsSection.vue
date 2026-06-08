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

<style scoped lang="scss">
.league-section {
  margin-bottom: 20px;

  :deep(.content-section-container) {
    background: #ffffff;
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: 14px;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04),
      0 4px 16px rgba(15, 23, 42, 0.04);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;

    &:hover {
      border-color: rgba(15, 23, 42, 0.12);
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05),
        0 8px 24px rgba(15, 23, 42, 0.06);
    }
  }

  :deep(.section-header) {
    border-bottom-color: rgba(15, 23, 42, 0.06);
  }
}

.result-card {
  border-radius: 12px;
  border: 1px solid rgba(15, 23, 42, 0.06);
  background: rgba(15, 23, 42, 0.015);
  transition: border-color 0.2s ease, background 0.2s ease;

  &:hover {
    border-color: rgba(15, 23, 42, 0.12);
    background: rgba(15, 23, 42, 0.03);
  }
}

:global(.body--dark) .league-section {
  :deep(.content-section-container) {
    background: #1e222a;
    border-color: rgba(255, 255, 255, 0.08);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.4),
      0 4px 16px rgba(0, 0, 0, 0.25);

    &:hover {
      border-color: rgba(255, 255, 255, 0.14);
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.45),
        0 8px 24px rgba(0, 0, 0, 0.35);
    }
  }

  :deep(.section-header) {
    border-bottom-color: rgba(255, 255, 255, 0.08);
  }
}

:global(.body--dark) .result-card {
  background: rgba(255, 255, 255, 0.03);
  border-color: rgba(255, 255, 255, 0.08);

  &:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.14);
  }
}
</style>

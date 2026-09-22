<template>
  <ContentSection
    title="Match Results"
    color="warning"
    icon="emoji_events"
    expandable
    v-model:is-opened="isOpened"
    v-bind="$attrs"
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
      >
        <q-card class="result-card" flat>
          <q-card-section class="q-pa-sm">
            <MatchResult :selectedGame="game" display-game-name />
          </q-card-section>
        </q-card>
      </div>
    </div>
    <div v-else class="text-center q-pa-lg text-grey-7">
      <q-icon name="sports_esports" size="36px" color="grey-5" class="q-mb-xs" />
      <div class="text-subtitle2 text-weight-bold">No results recorded yet</div>
      <div v-if="leagueStatus === 'PLAYING'" class="text-caption text-grey-6 q-mt-xs">
        Report match outcomes in the Report Results section below once games are played.
      </div>
      <div v-else class="text-caption text-grey-6 q-mt-xs">
        Match results will appear here once games have been selected and played.
      </div>
    </div>
  </ContentSection>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { storeToRefs } from 'pinia';
import ContentSection from 'components/base/ContentSection.vue';
import MatchResult from 'components/league/MatchResult.vue';
import { useMyLeagueStore } from 'src/composables/myLeague';

const { leagueStatus, selectedGamesWithResults } = storeToRefs(useMyLeagueStore());

const isOpened = ref(true);
</script>

<style scoped lang="scss">
.result-card {
  border-radius: var(--kenner-card-radius, 16px);
  border: 1px solid var(--kenner-border-color);
  background: rgba(0, 0, 0, 0.015);
}
</style>

<template>
  <ContentSection
    title="League Standings"
    color="info"
    icon="leaderboard"
    bordered
    expandable
    v-model:is-opened="isOpened"
    class="league-section"
  >
    <LeagueStandings />
  </ContentSection>
</template>

<script setup lang="ts">
import { ref, watchEffect } from 'vue';
import { storeToRefs } from 'pinia';
import LeagueStandings from 'components/league/LeagueStandings.vue';
import { useMyLeagueStore } from 'src/composables/myLeague';
import ContentSection from 'components/base/ContentSection.vue';

const { selectedGamesWithResults } = storeToRefs(useMyLeagueStore());

const isOpened = ref(false);

watchEffect(() => {
  isOpened.value = selectedGamesWithResults.value.length > 0;
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

</style>

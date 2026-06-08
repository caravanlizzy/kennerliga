<template>
  <ContentSection
    v-if="leagueStatus === 'PLAYING'"
    title="Report Results"
    color="accent"
    icon="publish"
    v-model:is-opened="isOpened"
    expandable
    bordered
    class="league-section"
  >
    <MatchResultTabs />
  </ContentSection>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { storeToRefs } from 'pinia';
import ContentSection from 'components/base/ContentSection.vue';
import MatchResultTabs from 'components/league/MatchResultTabs.vue';
import { useMyLeagueStore } from 'src/composables/myLeague';
import { useActionBar } from 'src/composables/actionBar';

const { leagueStatus } = storeToRefs(useMyLeagueStore());
const { setHint, reset } = useActionBar();

const isOpened = ref(false);

watch(
  leagueStatus,
  (status) => {
    isOpened.value = status === 'PLAYING';
    if (status === 'PLAYING') {
      reset();
      setHint('Games that are finished can be reported below.');
    }
  },
  { immediate: true }
);
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
</style>

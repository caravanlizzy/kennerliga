<template>
  <ContentSection
    title="Games - Picks and Bans"
    color="secondary"
    icon="groups"
    v-model:is-opened="isOpened"
    expandable
    bordered
    class="league-section"
  >
    <PlayerCard :all-members="members" />
  </ContentSection>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { storeToRefs } from 'pinia';
import ContentSection from 'components/base/ContentSection.vue';
import PlayerCard from 'components/league/PlayerCard.vue';
import { useMyLeagueStore } from 'src/composables/myLeague';

const { members } = storeToRefs(useMyLeagueStore());

const isOpened = ref(true);
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

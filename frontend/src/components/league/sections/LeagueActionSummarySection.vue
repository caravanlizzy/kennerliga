<template>
  <div v-bind="$attrs" class="league-action-summary-section">
    <div class="summary-header row items-center justify-between q-pb-xs q-mb-xs">
      <div class="row items-center q-gutter-x-xs text-grey-8">
        <q-icon name="history" size="18px" color="primary" />
        <span class="text-subtitle2 text-weight-bold tracking-tight text-primary">
          Action Summary
        </span>
      </div>
    </div>
    <LeagueActionSummary :league-id="leagueData?.id || leagueId" hide-title />
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import LeagueActionSummary from 'components/league/LeagueActionSummary.vue';
import { useMyLeagueStore } from 'src/composables/myLeague';

const { leagueId, leagueData } = storeToRefs(useMyLeagueStore());
</script>

<style scoped lang="scss">
.league-action-summary-section {
  width: 100%;
}
.summary-header {
  border-bottom: 1px solid var(--kenner-border-subtle, rgba(0, 0, 0, 0.06));
}
</style>

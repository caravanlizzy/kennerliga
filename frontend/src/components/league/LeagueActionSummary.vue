<template>
  <div class="league-action-summary">
    <LiveActionFeed
      :league-id="leagueId"
      hide-filters
      empty-text="No actions recorded yet for this league."
    />
  </div>
</template>

<script setup lang="ts">
import LiveActionFeed from 'components/ui/LiveActionFeed.vue';

interface Props {
  leagueId?: number;
}

defineProps<Props>();
</script>

<style scoped lang="scss">
.league-action-summary {
  width: 100%;
}
</style>

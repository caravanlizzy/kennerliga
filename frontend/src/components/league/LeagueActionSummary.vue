<template>
  <div class="league-action-summary">
    <div v-if="!hideTitle" class="row items-center q-gutter-x-xs q-mb-xs text-grey-8">
      <q-icon name="history" size="16px" color="primary" />
      <span class="text-caption text-weight-bold text-uppercase" style="letter-spacing: 0.05em">
        Action Summary
      </span>
    </div>
    <LiveActionFeed
      :league-id="leagueId"
      hide-filters
      hide-timestamp
      compact
      empty-text="No actions recorded yet."
    />
  </div>
</template>

<script setup lang="ts">
import LiveActionFeed from 'components/ui/LiveActionFeed.vue';

interface Props {
  leagueId?: number;
  hideTitle?: boolean;
}

withDefaults(defineProps<Props>(), {
  leagueId: undefined,
  hideTitle: false,
});
</script>

<style scoped lang="scss">
.league-action-summary {
  width: 100%;
}
</style>

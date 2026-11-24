<template>
  <div v-if="progress" class="season-progress-bar-container q-pa-sm q-px-md rounded-borders">
    <!-- Top row: Status info & Percentage -->
    <div class="row items-center justify-between no-wrap q-mb-xs">
      <div class="row items-center no-wrap q-gutter-x-xs text-caption text-weight-medium text-grey-8">
        <q-icon name="insights" size="16px" color="primary" />
        <span class="text-weight-bold text-dark">Season Progress</span>
        <span class="text-grey-6 gt-xs">•</span>
        <span class="text-caption text-grey-7 gt-xs">{{ phaseLabel }}</span>
      </div>
      <div class="row items-center no-wrap q-gutter-x-xs">
        <span class="text-subtitle2 text-weight-bolder text-primary">
          {{ formattedPercentage }}
        </span>
      </div>
    </div>

    <!-- The linear progress bar -->
    <q-linear-progress
      :value="progress.percentage / 100"
      rounded
      size="8px"
      color="primary"
      track-color="blue-1"
      class="season-progress-track q-mb-xs"
    >
      <KennerTooltip anchor="top middle" self="bottom middle">
        {{ formattedPercentage }} completed
      </KennerTooltip>
    </q-linear-progress>

    <!-- Bottom row: Metrics breakdown badges -->
    <div class="row items-center q-gutter-x-sm flex-wrap text-caption">
      <!-- Picks Metric -->
      <div
        class="metric-pill row items-center no-wrap q-px-xs rounded-borders"
        :class="isPicksComplete ? 'metric-pill--complete' : 'metric-pill--pending'"
      >
        <q-icon
          :name="isPicksComplete ? 'check_circle' : 'sports_esports'"
          size="13px"
          :color="isPicksComplete ? 'positive' : 'grey-7'"
          class="q-mr-xs"
        />
        <span>Picks: <strong>{{ progress.picks.current }}/{{ progress.picks.total }}</strong></span>
      </div>

      <!-- Bans Metric -->
      <div
        class="metric-pill row items-center no-wrap q-px-xs rounded-borders"
        :class="isBansComplete ? 'metric-pill--complete' : 'metric-pill--pending'"
      >
        <q-icon
          :name="isBansComplete ? 'check_circle' : 'block'"
          size="13px"
          :color="isBansComplete ? 'positive' : 'grey-7'"
          class="q-mr-xs"
        />
        <span>Bans: <strong>{{ progress.bans.current }}/{{ progress.bans.total }}</strong></span>
      </div>

      <!-- Games Metric -->
      <div
        class="metric-pill row items-center no-wrap q-px-xs rounded-borders"
        :class="isGamesComplete ? 'metric-pill--complete' : 'metric-pill--pending'"
      >
        <q-icon
          :name="isGamesComplete ? 'check_circle' : 'emoji_events'"
          size="13px"
          :color="isGamesComplete ? 'positive' : 'primary'"
          class="q-mr-xs"
        />
        <span>Games: <strong>{{ progress.reports.current }}/{{ progress.reports.total }}</strong></span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'SeasonProgressBar' });

import { computed } from 'vue';
import type { TSeasonProgress } from 'src/types';
import KennerTooltip from 'components/base/KennerTooltip.vue';

const props = defineProps<{
  progress?: TSeasonProgress | null;
  status?: string;
}>();

const formattedPercentage = computed(() => {
  if (!props.progress) return '0%';
  const p = props.progress.percentage;
  if (p === 0) return '0%';
  if (p === 100) return '100%';
  return p % 1 === 0 ? `${p}%` : `${p.toFixed(1)}%`;
});

const isPicksComplete = computed(() => {
  if (!props.progress) return false;
  return (
    props.progress.picks.total > 0 &&
    props.progress.picks.missing === 0
  );
});

const isBansComplete = computed(() => {
  if (!props.progress) return false;
  return (
    props.progress.bans.total > 0 &&
    props.progress.bans.missing === 0
  );
});

const isGamesComplete = computed(() => {
  if (!props.progress) return false;
  return (
    props.progress.reports.total > 0 &&
    props.progress.reports.missing === 0
  );
});

const phaseLabel = computed(() => {
  if (!props.progress) return '';
  if (props.progress.percentage >= 100 || props.status === 'DONE') {
    return 'Completed';
  }
  if (!isPicksComplete.value || !isBansComplete.value) {
    return 'Draft Phase (Picks & Bans)';
  }
  return 'Playing Phase';
});
</script>

<style scoped>
.season-progress-bar-container {
  background: var(--kenner-bg-subtle, rgba(0, 0, 0, 0.02));
  border: 1px solid var(--kenner-border-subtle, rgba(0, 0, 0, 0.08));
}

.metric-pill {
  font-size: 11px;
  line-height: 1.4;
  padding: 2px 6px;
  background: rgba(0, 0, 0, 0.04);
}

.metric-pill--complete {
  background: rgba(33, 186, 69, 0.08);
  color: var(--q-positive, #21ba45);
}

.metric-pill--pending {
  color: var(--kenner-text-secondary, #555);
}

body.body--dark .season-progress-bar-container {
  background: rgba(255, 255, 255, 0.03);
  border-color: rgba(255, 255, 255, 0.1);
}

body.body--dark .metric-pill {
  background: rgba(255, 255, 255, 0.06);
}

body.body--dark .metric-pill--complete {
  background: rgba(33, 186, 69, 0.15);
}
</style>

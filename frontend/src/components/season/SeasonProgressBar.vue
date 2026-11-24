<template>
  <div v-if="progress" class="season-progress-bar-container q-pa-sm q-px-md rounded-borders">
    <!-- Top row: Status info & Percentage -->
    <div class="row items-center justify-between no-wrap q-mb-xs">
      <div class="row items-center no-wrap q-gutter-x-xs text-caption text-weight-medium text-grey-8">
        <q-icon name="insights" size="16px" class="progress-header-icon" />
        <span class="text-weight-bold text-dark">Season Progress</span>
        <span class="text-grey-6 gt-xs">•</span>
        <span class="text-caption text-grey-7 gt-xs">{{ phaseLabel }}</span>
      </div>
      <div class="row items-center no-wrap q-gutter-x-xs">
        <span class="progress-percentage-text text-subtitle2 text-weight-bolder">
          {{ formattedPercentage }}
        </span>
      </div>
    </div>

    <!-- The linear progress bar -->
    <q-linear-progress
      :value="progress.percentage / 100"
      rounded
      size="8px"
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
        <span v-if="isPicksComplete">Picks</span>
        <span v-else>Picks: <strong>{{ progress.picks.current }}/{{ progress.picks.total }}</strong></span>
        <KennerTooltip>
          {{ progress.picks.current }} / {{ progress.picks.total }} picks completed
          {{ isPicksComplete ? '(Complete)' : `(${progress.picks.missing} remaining)` }}
        </KennerTooltip>
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
        <span v-if="isBansComplete">Bans</span>
        <span v-else>Bans: <strong>{{ progress.bans.current }}/{{ progress.bans.total }}</strong></span>
        <KennerTooltip>
          {{ progress.bans.current }} / {{ progress.bans.total }} bans completed
          {{ isBansComplete ? '(Complete)' : `(${progress.bans.missing} remaining)` }}
        </KennerTooltip>
      </div>

      <!-- Games Metric -->
      <div
        class="metric-pill row items-center no-wrap q-px-xs rounded-borders"
        :class="isGamesComplete ? 'metric-pill--complete' : 'metric-pill--pending'"
      >
        <q-icon
          :name="isGamesComplete ? 'check_circle' : 'emoji_events'"
          size="13px"
          :color="isGamesComplete ? 'positive' : 'amber-8'"
          class="q-mr-xs"
        />
        <span v-if="isGamesComplete">Games</span>
        <span v-else>Games: <strong>{{ progress.reports.current }}/{{ progress.reports.total }}</strong></span>
        <KennerTooltip>
          {{ progress.reports.current }} / {{ progress.reports.total }} games reported
          {{ isGamesComplete ? '(Complete)' : `(${progress.reports.missing} remaining)` }}
        </KennerTooltip>
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
  const p = Math.round(props.progress.percentage);
  return `${p}%`;
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

.progress-header-icon {
  color: var(--kenner-red, #ff7a59);
}

.progress-percentage-text {
  color: var(--kenner-red, #ff7a59);
}

.season-progress-track {
  height: 8px;
  border-radius: 4px;
}

.season-progress-track :deep(.q-linear-progress__track) {
  background: rgba(255, 122, 89, 0.14) !important;
  opacity: 1 !important;
}

.season-progress-track :deep(.q-linear-progress__model) {
  background: linear-gradient(90deg, #ff7a59 0%, #ec4899 100%) !important;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(236, 72, 153, 0.25);
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

body.body--dark .progress-header-icon,
body.body--dark .progress-percentage-text {
  color: #ff8c6f;
}

body.body--dark .season-progress-track :deep(.q-linear-progress__track) {
  background: rgba(255, 122, 89, 0.18) !important;
}

body.body--dark .season-progress-track :deep(.q-linear-progress__model) {
  background: linear-gradient(90deg, #ff7a59 0%, #ec4899 100%) !important;
  box-shadow: 0 1px 4px rgba(236, 72, 153, 0.4);
}

body.body--dark .metric-pill {
  background: rgba(255, 255, 255, 0.06);
}

body.body--dark .metric-pill--complete {
  background: rgba(33, 186, 69, 0.15);
}
</style>

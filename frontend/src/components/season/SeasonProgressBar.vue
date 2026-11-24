<template>
  <div v-if="progress" class="season-progress-bar full-width">
    <!-- Top row: Status info, compact inline metrics, and Percentage -->
    <div class="row items-center justify-between no-wrap q-mb-xs">
      <!-- Left side: Icon, title, phase -->
      <div class="row items-center no-wrap q-gutter-x-xs text-caption ellipsis">
        <q-icon name="insights" size="15px" class="progress-header-icon" />
        <span class="text-weight-bold text-dark">Season Progress</span>
        <span class="text-grey-5 gt-xs">•</span>
        <span class="text-caption text-grey-7 gt-xs ellipsis">{{ phaseLabel }}</span>
      </div>

      <!-- Right side: Mini inline metrics & percentage -->
      <div class="row items-center no-wrap q-gutter-x-sm shrink-0">
        <!-- Compact inline status indicators (desktop / tablet) -->
        <div class="row items-center no-wrap q-gutter-x-xs gt-xs text-caption">
          <!-- Picks -->
          <div
            class="mini-metric row items-center no-wrap q-px-xs rounded-borders"
            :class="isPicksComplete ? 'mini-metric--complete' : 'mini-metric--pending'"
          >
            <q-icon
              :name="isPicksComplete ? 'check_circle' : 'sports_esports'"
              size="12px"
              class="q-mr-xs"
            />
            <span v-if="isPicksComplete">Picks</span>
            <span v-else>Picks: {{ progress.picks.current }}/{{ progress.picks.total }}</span>
            <KennerTooltip>
              {{ progress.picks.current }} / {{ progress.picks.total }} picks completed
              {{ isPicksComplete ? '(Complete)' : `(${progress.picks.missing} remaining)` }}
            </KennerTooltip>
          </div>

          <!-- Bans -->
          <div
            class="mini-metric row items-center no-wrap q-px-xs rounded-borders"
            :class="isBansComplete ? 'mini-metric--complete' : 'mini-metric--pending'"
          >
            <q-icon
              :name="isBansComplete ? 'check_circle' : 'block'"
              size="12px"
              class="q-mr-xs"
            />
            <span v-if="isBansComplete">Bans</span>
            <span v-else>Bans: {{ progress.bans.current }}/{{ progress.bans.total }}</span>
            <KennerTooltip>
              {{ progress.bans.current }} / {{ progress.bans.total }} bans completed
              {{ isBansComplete ? '(Complete)' : `(${progress.bans.missing} remaining)` }}
            </KennerTooltip>
          </div>

          <!-- Games -->
          <div
            class="mini-metric row items-center no-wrap q-px-xs rounded-borders"
            :class="isGamesComplete ? 'mini-metric--complete' : 'mini-metric--pending'"
          >
            <q-icon
              :name="isGamesComplete ? 'check_circle' : 'emoji_events'"
              size="12px"
              class="q-mr-xs"
            />
            <span v-if="isGamesComplete">Games</span>
            <span v-else>Games: {{ progress.reports.current }}/{{ progress.reports.total }}</span>
            <KennerTooltip>
              {{ progress.reports.current }} / {{ progress.reports.total }} games reported
              {{ isGamesComplete ? '(Complete)' : `(${progress.reports.missing} remaining)` }}
            </KennerTooltip>
          </div>
        </div>

        <!-- Percentage display -->
        <span class="progress-percentage-text text-weight-bolder">
          {{ formattedPercentage }}
        </span>
      </div>
    </div>

    <!-- The linear progress bar track -->
    <q-linear-progress
      :value="progress.percentage / 100"
      rounded
      size="4px"
      class="season-progress-track"
    >
      <KennerTooltip anchor="top middle" self="bottom middle">
        {{ formattedPercentage }} completed • {{ phaseLabel }}
      </KennerTooltip>
    </q-linear-progress>

    <!-- Mobile-only compact metrics row (xs only) -->
    <div
      class="row items-center justify-between lt-sm q-mt-xs text-caption text-grey-7"
      style="font-size: 11px;"
    >
      <span :class="{ 'text-positive text-weight-medium': isPicksComplete }">
        {{ isPicksComplete ? 'Picks ✓' : `Picks: ${progress.picks.current}/${progress.picks.total}` }}
      </span>
      <span :class="{ 'text-positive text-weight-medium': isBansComplete }">
        {{ isBansComplete ? 'Bans ✓' : `Bans: ${progress.bans.current}/${progress.bans.total}` }}
      </span>
      <span :class="{ 'text-positive text-weight-medium': isGamesComplete }">
        {{ isGamesComplete ? 'Games ✓' : `Games: ${progress.reports.current}/${progress.reports.total}` }}
      </span>
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
    return 'Draft Phase';
  }
  return 'Playing Phase';
});
</script>

<style scoped>
.season-progress-bar {
  background: transparent;
}

.shrink-0 {
  flex-shrink: 0;
}

.progress-header-icon {
  color: var(--kenner-info-text, #1d4ed8);
}

.progress-percentage-text {
  font-size: 13px;
  color: var(--kenner-info-text, #1d4ed8);
}

.season-progress-track {
  height: 4px;
  border-radius: 2px;
}

.season-progress-track :deep(.q-linear-progress__track) {
  background: var(--kenner-surface-strong, rgba(0, 0, 0, 0.08)) !important;
  opacity: 1 !important;
}

.season-progress-track :deep(.q-linear-progress__model) {
  background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important;
  border-radius: 2px;
}

.mini-metric {
  font-size: 11px;
  line-height: 1.3;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.03);
  border: 1px solid var(--kenner-border-subtle, rgba(0, 0, 0, 0.06));
}

.mini-metric--complete {
  background: rgba(34, 197, 94, 0.08);
  border-color: rgba(34, 197, 94, 0.2);
  color: var(--kenner-success-text, #15803d);
}

.mini-metric--pending {
  color: var(--kenner-text-secondary, #475569);
}

body.body--dark .progress-header-icon {
  color: #60a5fa;
}

body.body--dark .progress-percentage-text {
  color: #60a5fa;
}

body.body--dark .season-progress-track :deep(.q-linear-progress__track) {
  background: rgba(255, 255, 255, 0.1) !important;
}

body.body--dark .season-progress-track :deep(.q-linear-progress__model) {
  background: linear-gradient(90deg, #60a5fa 0%, #3b82f6 100%) !important;
}

body.body--dark .mini-metric {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.08);
  color: #94a3b8;
}

body.body--dark .mini-metric--complete {
  background: rgba(34, 197, 94, 0.15);
  border-color: rgba(34, 197, 94, 0.3);
  color: #4ade80;
}
</style>

<template>
  <q-page class="bg-white">
    <div
      class="q-px-md q-py-sm row items-center justify-between no-wrap border-bottom-subtle"
    >
      <div class="row items-center no-wrap q-gutter-x-sm">
        <div class="text-h6 text-weight-bold text-dark">Seasons</div>
        <div
          v-if="isLiveSeason || isRunningSeason"
          class="season-live-badge row items-center no-wrap q-gutter-x-xs"
        >
          <span class="status-dot" />
          <span class="live-text">Running</span>
        </div>
      </div>
      <div
        v-if="!loading || selectedSeasonId"
        class="row no-wrap items-center q-gutter-x-xs"
      >
        <div style="min-width: 76px">
          <KennerSelect
            v-model="selectedSeasonYear"
            :options="seasonYearOptions"
            dense
            emit-value
            map-options
            :disable="loading && !selectedSeasonId"
            class="compact-select"
          />
        </div>
        <div style="min-width: 62px">
          <KennerSelect
            v-model="selectedSeasonMonth"
            :options="seasonMonthOptions"
            dense
            emit-value
            map-options
            :disable="loading && !selectedSeasonId"
            class="compact-select"
          />
        </div>
        <KennerButton
          v-if="currentSeasonId && selectedSeasonId !== currentSeasonId"
          flat
          round
          dense
          icon="today"
          color="positive"
          @click="homeSeasonStore.selectCurrentSeason"
        >
          <q-tooltip>Current Season</q-tooltip>
        </KennerButton>
        <KennerButton
          v-if="selectedSeasonId"
          flat
          round
          dense
          icon="visibility"
          color="primary"
          :to="{ name: 'season-overview', params: { id: selectedSeasonId } }"
        >
          <q-tooltip>Season Overview</q-tooltip>
        </KennerButton>
      </div>
    </div>
    <div
      v-if="
        (isLiveSeason || isRunningSeason) &&
        selectedSeasonProgress &&
        selectedSeasonId &&
        !loading
      "
      class="q-px-md q-py-xs q-my-xs"
    >
      <div class="season-progress-card">
        <SeasonProgressBar
          :progress="selectedSeasonProgress"
          :status="selectedSeason?.status"
        />
      </div>
    </div>
    <SeasonStandings v-if="selectedSeasonId" :seasonId="selectedSeasonId" />
    <div v-else-if="loading" class="flex flex-center q-pa-xl">
      <LoadingSpinner text="Loading seasons..." />
    </div>
  </q-page>
</template>

<script setup lang="ts">
defineOptions({ name: 'SeasonsMobilePage' });

import { computed, onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import KennerButton from 'components/base/KennerButton.vue';
import SeasonStandings from 'components/season/SeasonStandings.vue';
import SeasonProgressBar from 'components/season/SeasonProgressBar.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import { useHomeSeasonStore } from 'stores/homeSeasonStore';

const homeSeasonStore = useHomeSeasonStore();

const {
  selectedSeasonYear,
  selectedSeasonMonth,
  loading,
  seasonYearOptions,
  seasonMonthOptions,
  selectedSeasonId,
  currentSeasonId,
  selectedSeason,
  selectedSeasonProgress,
} = storeToRefs(homeSeasonStore);

const isRunningSeason = computed(
  () => selectedSeason.value?.status === 'RUNNING'
);

const isLiveSeason = computed(
  () =>
    currentSeasonId.value != null &&
    selectedSeasonId.value != null &&
    currentSeasonId.value === selectedSeasonId.value
);

onMounted(() => {
  void homeSeasonStore.init();
});
</script>

<style scoped>
.border-bottom-subtle {
  border-bottom: 1px solid var(--kenner-border-subtle);
}

.compact-select {
  padding: 0 8px;
  min-height: 32px;
  height: 32px;
  border-radius: 8px;
  font-size: 0.85rem;
}

.compact-select :deep(.q-field__control) {
  min-height: 32px !important;
  height: 32px !important;
}

.compact-select :deep(.q-field__native) {
  font-size: 0.85rem;
  font-weight: 600;
}

.season-progress-card {
  background: var(--kenner-surface-subtle, #f8fafc);
  border: 1px solid var(--kenner-border-subtle);
  border-radius: 12px;
  padding: 8px 12px;
}

.body--dark .season-progress-card {
  background: var(--kenner-surface-card, #1e293b);
}

.season-live-badge {
  background: var(--kenner-success-bg, rgba(34, 197, 94, 0.08));
  color: var(--kenner-success-text, #15803d);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.3px;
  text-transform: uppercase;
  border-radius: 9999px;
  padding: 1px 7px;
  border: 1px solid rgba(34, 197, 94, 0.25);
  line-height: 1.4;
}

.status-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background-color: currentColor;
  opacity: 0.85;
  display: inline-block;
}

.body--dark .season-live-badge {
  border-color: rgba(74, 222, 128, 0.3);
}
</style>

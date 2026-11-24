<template>
  <q-page class="bg-white">
    <div
      class="q-pa-md row items-center justify-between no-wrap border-bottom-subtle"
    >
      <div class="row items-center no-wrap q-gutter-x-sm">
        <div class="text-h5 text-weight-bold text-dark">Seasons</div>
        <div
          v-if="isLiveSeason || isRunningSeason"
          class="season-live-badge row items-center no-wrap q-gutter-x-xs q-px-sm q-py-xs rounded-borders"
        >
          <span class="pulse-dot" />
          <span class="text-weight-bolder text-uppercase live-text">Running</span>
        </div>
      </div>
      <div
        v-if="!loading || selectedSeasonId"
        class="row no-wrap items-center q-gutter-x-sm"
      >
        <div style="min-width: 80px">
          <KennerSelect
            v-model="selectedSeasonYear"
            :options="seasonYearOptions"
            dense
            label="Year"
            emit-value
            map-options
            :disable="loading && !selectedSeasonId"
          />
        </div>
        <div style="min-width: 100px">
          <KennerSelect
            v-model="selectedSeasonMonth"
            :options="seasonMonthOptions"
            dense
            label="Month"
            emit-value
            map-options
            :disable="loading && !selectedSeasonId"
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
      v-if="(isLiveSeason || isRunningSeason) && selectedSeasonProgress && selectedSeasonId && !loading"
      class="q-px-md q-pt-sm"
    >
      <SeasonProgressBar
        :progress="selectedSeasonProgress"
        :status="selectedSeason?.status"
      />
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

.season-live-badge {
  background: rgba(33, 186, 69, 0.12);
  color: var(--q-positive, #21ba45);
  font-size: 11px;
  letter-spacing: 0.5px;
  border: 1px solid rgba(33, 186, 69, 0.3);
}

.pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: var(--q-positive, #21ba45);
  box-shadow: 0 0 0 0 rgba(33, 186, 69, 0.7);
  animation: pulse-ring 1.8s cubic-bezier(0.455, 0.03, 0.515, 0.955) infinite;
  display: inline-block;
}

@keyframes pulse-ring {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(33, 186, 69, 0.7);
  }
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 6px rgba(33, 186, 69, 0);
  }
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(33, 186, 69, 0);
  }
}
</style>

<template>
  <q-page class="bg-white">
    <div
      class="q-pa-md row items-center justify-between no-wrap border-bottom-subtle"
    >
      <div class="text-h5 text-weight-bold text-dark">Seasons</div>
      <div
        v-if="!loadingSeasonInit"
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
          />
        </div>
        <q-icon name="military_tech" size="sm" color="primary" />
      </div>
    </div>
    <SeasonStandings v-if="!loadingSeasonInit" :seasonId="selectedSeasonId" />
    <div v-else class="flex flex-center q-pa-xl">
      <LoadingSpinner text="Loading seasons..." />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import LoadingSpinner from 'components/base/LoadingSpinner.vue';

defineOptions({ name: 'SeasonsMobilePage' });
import { ref, computed, onMounted, watch } from 'vue';
import SeasonStandings from 'components/season/SeasonStandings.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import {
  fetchAvailableYears,
  fetchCurrentSeasonId,
  fetchSeason,
  fetchSeasons
} from 'src/services/seasonService';
import type { TSeasonDto } from 'src/types';

const availableYears = ref<number[]>([]);
const seasonsForYear = ref<TSeasonDto[]>([]);
const selectedSeasonYear = ref<number | null>(null);
const selectedSeasonMonth = ref<number | null>(null);
const loadingSeasonInit = ref(false);

const seasonYearOptions = computed(() =>
  [...availableYears.value]
    .sort((a, b) => b - a)
    .map((y) => ({ label: String(y), value: y }))
);

const seasonMonthOptions = computed(() => {
  return seasonsForYear.value
    .map((s) => s.month)
    .sort((a, b) => a - b)
    .map((m) => ({
      label: m,
      value: m,
    }));
});

const selectedSeasonId = computed(() => {
  const found = seasonsForYear.value.find(
    (s) => s.month === selectedSeasonMonth.value
  );
  return found ? found.id : null;
});

watch(selectedSeasonYear, async (newYear) => {
  if (newYear) {
    const seasons = await fetchSeasons({ year: newYear });
    seasonsForYear.value = seasons;

    if (seasons.length > 0) {
      const months = seasons.map((s) => s.month);
      if (
        !selectedSeasonMonth.value ||
        !months.includes(selectedSeasonMonth.value)
      ) {
        selectedSeasonMonth.value = Math.max(...months);
      }
    } else {
      selectedSeasonMonth.value = null;
    }
  } else {
    seasonsForYear.value = [];
    selectedSeasonMonth.value = null;
  }
});

onMounted(async () => {
  loadingSeasonInit.value = true;
  try {
    // 1. Fetch current season ID first as requested
    const currentSeasonId = await fetchCurrentSeasonId();

    if (currentSeasonId) {
      const season = await fetchSeason(currentSeasonId);
      if (season) {
        seasonsForYear.value = await fetchSeasons({ year: season.year });

        selectedSeasonYear.value = season.year;
        selectedSeasonMonth.value = season.month;
      }
    }

    // Stop loading the spinner if we have a seasonId and basic year info
    if (selectedSeasonId.value) {
      loadingSeasonInit.value = false;
    }

    // 2. Then fetch years (lower priority)
    availableYears.value = await fetchAvailableYears();

    // 3. Fallback
    if (!selectedSeasonId.value && availableYears.value.length > 0) {
      const year = availableYears.value[0];
      const seasons = await fetchSeasons({ year });
      seasonsForYear.value = seasons;

      selectedSeasonYear.value = year;
      if (seasons.length > 0) {
        selectedSeasonMonth.value = Math.max(...seasons.map(s => s.month));
      }
    }
  } finally {
    loadingSeasonInit.value = false;
  }
});
</script>

<style scoped>
.border-bottom-subtle {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}
</style>

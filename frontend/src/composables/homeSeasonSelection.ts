import { computed, ref, watch, type Ref } from 'vue';
import {
  fetchAvailableYears,
  fetchCurrentSeasonId,
  fetchSeason,
  fetchSeasons,
} from 'src/services/seasonService';
import type { TSeasonDto } from 'src/types';

export function homeSeasonSelection(isAuthenticated: Ref<boolean>) {
  const selectedYear = ref(new Date().getFullYear());
  const availableYears = ref<number[]>([]);
  const loadingSeasonInit = ref(false);

  const seasonsForYear = ref<TSeasonDto[]>([]);
  const selectedSeasonYear = ref<number | null>(null);
  const selectedSeasonMonth = ref<number | null>(null);

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

      // If current selected month is not in new seasons, pick the latest month
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

  const initSeasonSelection = async () => {
    if (!isAuthenticated.value) return;

    loadingSeasonInit.value = true;
    try {
      // 1. Fetch current season ID first to get started as soon as possible
      const currentSeasonId = await fetchCurrentSeasonId();

      if (currentSeasonId) {
        const season = await fetchSeason(currentSeasonId);
        if (season) {
          selectedYear.value = season.year;

          // We fetch seasons for the selected year immediately to have them ready for the dropdowns
          seasonsForYear.value = await fetchSeasons({ year: season.year });

          selectedSeasonYear.value = season.year;
          selectedSeasonMonth.value = season.month;
        }
      }

      // We can stop loading the spinner here if we have a seasonId and basic year info
      if (selectedSeasonId.value) {
        loadingSeasonInit.value = false;
      }

      // 2. Then fetch years (lower priority)
      availableYears.value = await fetchAvailableYears();

      // 3. Handle fallback if no currentSeasonId was found
      if (!selectedSeasonId.value && availableYears.value.length > 0) {
        const year = availableYears.value[0];
        selectedYear.value = year;

        const seasons = await fetchSeasons({ year });
        seasonsForYear.value = seasons;

        selectedSeasonYear.value = year;
        if (seasons.length > 0) {
          selectedSeasonMonth.value = Math.max(...seasons.map((s) => s.month));
        }
      }
    } finally {
      loadingSeasonInit.value = false;
    }
  };

  return {
    selectedYear,
    availableYears,
    loadingSeasonInit,

    selectedSeasonYear,
    selectedSeasonMonth,
    selectedSeasonId,

    seasonYearOptions,
    seasonMonthOptions,

    initSeasonSelection,
  };
}

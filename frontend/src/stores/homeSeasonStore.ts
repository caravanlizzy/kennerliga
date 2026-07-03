// stores/homeSeasonStore.ts
import { defineStore } from 'pinia';
import { computed, ref, watch } from 'vue';
import {
  fetchAvailableYears,
  fetchCurrentSeasonId,
  fetchSeason,
  fetchSeasons,
} from 'src/services/seasonService';
import type { TSeasonDto } from 'src/types';

/**
 * Pinia store powering the "Seasons" block on the authenticated home dashboard.
 *
 * Design goals (mirrors the stale-while-revalidate pattern already used by
 * `leagueStore`):
 *
 * - Persist the user's selection (`selectedSeasonYear`, `selectedSeasonMonth`)
 *   and the fetched reference data (`availableYears`, `seasonsByYear`,
 *   `currentSeasonId`) across component unmounts, so navigating away from and
 *   back to the home page renders instantly from cache.
 * - Distinguish a blocking `loading` state (only true on the very first init,
 *   when there is nothing to show yet) from a non-blocking `refreshing` state
 *   (background refresh while cached data is still visible).
 * - Dedupe concurrent init/refresh calls via `initPromise` / `refreshPromise`.
 * - Cache seasons per year in a `seasonsByYear` map so switching year is
 *   instantaneous on repeat visits and doesn't refetch what we already have.
 *
 * The store deliberately exposes the same shape the old `homeSeasonSelection`
 * composable did, so its consumers (`AuthenticatedHomeDashboard`,
 * `HomeSeasonSection`) can be migrated with minimal churn.
 */
export const useHomeSeasonStore = defineStore('homeSeason', () => {
  // --- Selection state (persisted across mounts) ---
  const selectedYear = ref<number>(new Date().getFullYear());
  const selectedSeasonYear = ref<number | null>(null);
  const selectedSeasonMonth = ref<number | null>(null);

  // --- Reference data (cached) ---
  const availableYears = ref<number[]>([]);
  const seasonsByYear = ref<Record<number, TSeasonDto[]>>({});
  const currentSeasonId = ref<number | null>(null);

  // --- Loading flags ---
  // `loading` is only true when we have nothing to display yet (very first
  // init). `refreshing` is true during background refreshes on subsequent
  // visits — consumers can ignore it or show a subtle indicator.
  const loading = ref(false);
  const refreshing = ref(false);
  const initialized = ref(false);

  // In-flight promises for deduping concurrent callers.
  let initPromise: Promise<void> | null = null;
  let refreshPromise: Promise<void> | null = null;

  // --- Derived data ---
  const seasonsForYear = computed<TSeasonDto[]>(() => {
    const y = selectedSeasonYear.value;
    if (y == null) return [];
    return seasonsByYear.value[y] ?? [];
  });

  const seasonYearOptions = computed(() =>
    [...availableYears.value]
      .sort((a, b) => b - a)
      .map((y) => ({ label: String(y), value: y }))
  );

  const seasonMonthOptions = computed(() =>
    seasonsForYear.value
      .map((s) => s.month)
      .sort((a, b) => a - b)
      .map((m) => ({ label: m, value: m }))
  );

  const selectedSeasonId = computed<number | null>(() => {
    const found = seasonsForYear.value.find(
      (s) => s.month === selectedSeasonMonth.value
    );
    return found ? found.id : null;
  });

  // --- Internal fetch helpers -----------------------------------------------

  /**
   * Ensure `seasonsByYear[year]` is populated. Fetches (and caches) on first
   * request; subsequent calls are no-ops unless `force` is set (used by
   * background refresh).
   */
  async function ensureSeasonsForYear(year: number, force = false): Promise<TSeasonDto[]> {
    if (!force && seasonsByYear.value[year]) {
      return seasonsByYear.value[year] as TSeasonDto[];
    }
    const seasons = await fetchSeasons({ year });
    seasonsByYear.value = { ...seasonsByYear.value, [year]: seasons };
    return seasons;
  }

  /**
   * Core fetch used by both the initial (blocking) load and background
   * refreshes. When `background` is true, the blocking `loading` flag is not
   * flipped, so cached UI stays visible.
   */
  async function fetchAll(background: boolean): Promise<void> {
    if (background) refreshing.value = true;
    else loading.value = true;

    try {
      // 1. Current season → drives default selection.
      const fetchedCurrentSeasonId = await fetchCurrentSeasonId();
      currentSeasonId.value = fetchedCurrentSeasonId;

      let resolvedYear: number | null = null;
      let resolvedMonth: number | null = null;

      if (fetchedCurrentSeasonId) {
        const season = await fetchSeason(fetchedCurrentSeasonId);
        if (season) {
          resolvedYear = season.year;
          resolvedMonth = season.month;
          // Prefetch seasons for the resolved year so dropdowns are ready.
          await ensureSeasonsForYear(season.year, background);
        }
      }

      // 2. Available years (lower priority).
      availableYears.value = await fetchAvailableYears();

      // 3. Fallback if there is no current season: pick the most recent year.
      if (resolvedYear == null && availableYears.value.length > 0) {
        const fallbackYear = availableYears.value[0] as number;
        resolvedYear = fallbackYear;
        const seasons = await ensureSeasonsForYear(fallbackYear, background);
        if (seasons.length > 0) {
          resolvedMonth = Math.max(...seasons.map((s) => s.month));
        }
      }

      // 4. Apply selection.
      //    - On first init: always seed selection from server-resolved values.
      //    - On background refresh: only seed if the user hasn't picked
      //      anything yet, so we never clobber an active user selection.
      const shouldSeedSelection =
        !background || selectedSeasonYear.value == null || selectedSeasonMonth.value == null;

      if (shouldSeedSelection && resolvedYear != null) {
        selectedYear.value = resolvedYear;
        selectedSeasonYear.value = resolvedYear;
        selectedSeasonMonth.value = resolvedMonth;
      }
    } finally {
      if (background) refreshing.value = false;
      else loading.value = false;
    }
  }

  // --- Public actions --------------------------------------------------------

  /**
   * Stale-while-revalidate init.
   *
   * - First ever call: performs a blocking fetch (`loading = true`) so callers
   *   can `await init()` and then render.
   * - Subsequent calls (store already has data): returns immediately with the
   *   cached data, and kicks off a non-blocking background refresh so any
   *   server-side changes propagate reactively.
   */
  async function init(): Promise<void> {
    if (initialized.value) {
      void refreshInBackground();
      return;
    }
    if (initPromise) return initPromise;

    initPromise = (async () => {
      try {
        await fetchAll(false);
        initialized.value = true;
      } finally {
        initPromise = null;
      }
    })();
    return initPromise;
  }

  /**
   * Non-blocking refresh. At most one in flight at a time. Errors are
   * swallowed on purpose — the cached data stays visible.
   */
  function refreshInBackground(): Promise<void> {
    if (refreshPromise) return refreshPromise;
    refreshPromise = (async () => {
      try {
        await fetchAll(true);
      } catch {
        // Ignore — cached data remains visible.
      } finally {
        refreshPromise = null;
      }
    })();
    return refreshPromise;
  }

  // --- Reactions -------------------------------------------------------------

  /**
   * When the user picks a different year in the dropdown, make sure seasons
   * for that year are loaded (cached after the first fetch) and reconcile the
   * selected month.
   */
  watch(selectedSeasonYear, async (newYear, oldYear) => {
    if (newYear === oldYear) return;
    if (newYear == null) {
      selectedSeasonMonth.value = null;
      return;
    }
    const seasons = await ensureSeasonsForYear(newYear);
    if (seasons.length === 0) {
      selectedSeasonMonth.value = null;
      return;
    }
    const months = seasons.map((s) => s.month);
    if (
      selectedSeasonMonth.value == null ||
      !months.includes(selectedSeasonMonth.value)
    ) {
      selectedSeasonMonth.value = Math.max(...months);
    }
  });

  /**
   * Explicit reset — handy on logout. Not called automatically; the consuming
   * layer decides when the cache should be invalidated.
   */
  function reset() {
    selectedYear.value = new Date().getFullYear();
    selectedSeasonYear.value = null;
    selectedSeasonMonth.value = null;
    availableYears.value = [];
    seasonsByYear.value = {};
    currentSeasonId.value = null;
    loading.value = false;
    refreshing.value = false;
    initialized.value = false;
    initPromise = null;
    refreshPromise = null;
  }

  return {
    // state
    selectedYear,
    selectedSeasonYear,
    selectedSeasonMonth,
    availableYears,
    seasonsByYear,
    currentSeasonId,
    loading,
    refreshing,
    initialized,

    // getters
    seasonsForYear,
    seasonYearOptions,
    seasonMonthOptions,
    selectedSeasonId,

    // actions
    init,
    refreshInBackground,
    reset,
  };
});

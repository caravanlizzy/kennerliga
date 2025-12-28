<template>
  <div :class="isMobile ? 'q-pa-sm' : 'q-pa-md'" class="column season-standings">
    <!-- Filters -->
    <div
      class="row q-pa-sm q-gutter-x-sm items-center justify-between filters-container bg-grey-1 rounded-borders q-mb-lg no-wrap"
    >
      <div class="row items-center no-wrap col">
        <q-icon name="event" color="grey-7" size="xs" class="q-mr-xs" />
        <KennerSelect
          v-model="selectedYear"
          :options="yearOptions"
          label="Year"
          dense
          filled
          emit-value
          map-options
          :disable="loadingSeasons"
          class="col"
          style="min-width: 80px"
          hide-bottom-space
        />
      </div>

      <div class="row items-center no-wrap col">
        <q-icon name="calendar_month" color="grey-7" size="xs" class="q-mr-xs" />
        <KennerSelect
          v-model="selectedMonth"
          :options="monthOptions"
          label="Month"
          dense
          filled
          emit-value
          map-options
          :disable="loadingSeasons || !selectedYear || monthOptions.length === 0"
          class="col"
          style="min-width: 80px"
          hide-bottom-space
        />
      </div>
    </div>

    <!-- State primary -->
    <LoadingSpinner v-if="loadingSeasons" />

    <!-- Leagues + matrices -->
    <div v-if="!selectedSeasonId && !loadingSeasons" class="column items-center q-pa-xl text-grey-6">
      <q-icon name="info_outline" size="48px" class="q-mb-md" />
      <div class="text-h6">No season selected</div>
      <div>Please select year and month that contain a league.</div>
    </div>

    <LoadingSpinner v-else-if="loadingLeagues" />

    <div v-else-if="leagues.length === 0 && selectedSeasonId" class="column items-center q-pa-xl text-grey-6">
       <q-icon name="warning_amber" size="48px" class="q-mb-md" />
       <div class="text-h6">No leagues found</div>
       <div>No leagues for this season.</div>
    </div>

    <div v-else class="column q-gutter-y-xl">
      <div v-for="league in leagues" :key="league.id" class="league-wrapper">
        <div class="row items-center q-mb-md q-px-sm">
          <div class="league-badge q-mr-md">
            {{ league.level }}
          </div>
          <div class="column">
            <div class="text-h6 text-weight-bold text-grey-9 line-height-1">
              League {{ league.level }}
            </div>
            <div class="text-caption text-grey-6 uppercase letter-spacing-1">Division Standings</div>
          </div>
          <q-space />
          <KennerButton flat round icon="info" color="grey-4" size="sm">
            <KennerTooltip>Current standings for League {{ league.level }}</KennerTooltip>
          </KennerButton>
        </div>
        <div class="matrix-container rounded-borders overflow-hidden">
          <LeagueStandingsMatrix :leagueId="league.id" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import LeagueStandingsMatrix from 'components/league/LeagueStandingsMatrix.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import { api } from 'boot/axios';
import KennerSelect from 'components/base/KennerSelect.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import { useResponsive } from 'src/composables/responsive';

const { isMobile } = useResponsive();

interface Season {
  id: number;
  year: number;
  month: number;
  status: string;
  name?: string;
}

interface League {
  id: number;
  name: string;
  level: number;
}

const seasonsWithLeagues = ref<Season[]>([]);
const loadingSeasons = ref(false);

const selectedYear = ref<number | null>(null);
const selectedMonth = ref<number | null>(null);
const selectedSeasonId = ref<number | null>(null);

const leagues = ref<League[]>([]);
const loadingLeagues = ref(false);

const monthNames = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
];

const yearOptions = computed(() =>
  Array.from(new Set(seasonsWithLeagues.value.map((s) => s.year)))
    .sort((a, b) => b - a)
    .map((y) => ({ label: String(y), value: y }))
);

const monthOptions = computed(() => {
  if (!selectedYear.value) return [];

  const monthsForYear = seasonsWithLeagues.value
    .filter((s) => s.year === selectedYear.value)
    .map((s) => s.month);

  const uniqueMonths = Array.from(new Set(monthsForYear)).sort((a, b) => a - b);

  return uniqueMonths.map((m) => ({
    label: String(m),
    value: m,
  }));
});

// Load all seasons, then filter only those that have at least one league
async function loadSeasonsWithLeagues() {
  loadingSeasons.value = true;
  try {
    const { data } = await api.get(
      'result/match-results/seasons-with-results/'
    );
    seasonsWithLeagues.value = data;
    // Preselect the latest (year, month) that actually has leagues
    if (seasonsWithLeagues.value.length > 0) {
      const latest = [...seasonsWithLeagues.value].sort((a, b) => {
        if (a.year !== b.year) return b.year - a.year;
        return b.month - a.month;
      })[0];

      selectedYear.value = latest.year;
      selectedMonth.value = latest.month;
    }
  } catch (err) {
    console.log(err);
  } finally {
    loadingSeasons.value = false;
  }
}

async function loadLeaguesForSeason(seasonId: number) {
  loadingLeagues.value = true;
  try {
    const { data } = await api.get<League[]>('league/leagues', {
      params: { season: seasonId },
    });
    leagues.value = data;
  } finally {
    loadingLeagues.value = false;
  }
}

// When year changes, reset month
watch(selectedYear, (newVal, oldVal) => {
  if (oldVal !== null && newVal !== oldVal) {
    selectedMonth.value = null;
  }
});

// When year or month changes, compute the season and load leagues
watch([selectedYear, selectedMonth], ([year, month]) => {
  if (!year || !month) {
    selectedSeasonId.value = null;
    leagues.value = [];
    return;
  }

  const season = seasonsWithLeagues.value.find(
    (s) => s.year === year && s.month === month
  );

  selectedSeasonId.value = season ? season.id : null;
});

watch(selectedSeasonId, (id) => {
  if (!id) {
    leagues.value = [];
    return;
  }
  loadLeaguesForSeason(id);
});

onMounted(() => {
  loadSeasonsWithLeagues();
});
</script>

<style scoped lang="scss">
.season-standings {
  max-width: 1200px;
  margin: 0 auto;
}

.filters-container {
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.league-badge {
  background: var(--q-primary);
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.2rem;
  box-shadow: 0 2px 4px rgba(var(--q-primary), 0.3);
}

.line-height-1 {
  line-height: 1;
}

.letter-spacing-1 {
  letter-spacing: 1px;
}

.uppercase {
  text-transform: uppercase;
}

.matrix-container {
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.05);
}
</style>

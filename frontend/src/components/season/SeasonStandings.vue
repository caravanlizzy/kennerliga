<template>
  <ContentSection title="Seasons" color="secondary">
    <div :class="isMobile ? '' : 'q-pa-md q-gutter-md'" class="column">
      <!-- Filters -->
      <!-- Filters -->
      <div class="row q-gutter-sm items-end">
        <KennerSelect
          v-model="selectedYear"
          :options="yearOptions"
          label="Year"
          dense
          outlined
          emit-value
          map-options
          :loading="loadingSeasons"
          style="max-width: 140px"
        />

        <KennerSelect
          v-model="selectedMonth"
          :options="monthOptions"
          label="Month"
          dense
          outlined
          emit-value
          map-options
          :disable="!selectedYear || monthOptions.length === 0"
          :loading="loadingSeasons"
          style="max-width: 180px"
        />

        <div class="text-caption text-grey-7 q-ml-sm q-mt-xs">
          See current standings for all active leagues. Use the selects to view past seasons.
        </div>
      </div>


      <!-- State info -->
      <div v-if="loadingSeasons" class="text-grey-7">Loading seasons…</div>

      <q-separator />

      <!-- Leagues + matrices -->
      <div v-if="!selectedSeasonId" class="text-grey-7">
        Please select year and month that contain a league.
      </div>

      <div v-else-if="loadingLeagues" class="text-grey-7">Loading leagues…</div>

      <div v-else-if="leagues.length === 0" class="text-grey-7">
        No leagues for this season. (Should not happen if filters are correct.)
      </div>

      <div v-else class="column">
        <div v-for="league in leagues" :key="league.id">
          <q-badge class="q-ml-md q-mt-xs" outlined dense> League{{league.level}}</q-badge>
          <LeagueStandingsMatrix
            class="q-mb-md"
            :leagueId="league.id"
          />
        </div>
      </div>
    </div>
  </ContentSection>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import SideAccentBox from 'components/base/SideAccentBox.vue';
import LeagueStandingsMatrix from 'components/league/LeagueStandingsMatrix.vue';
import { api } from 'boot/axios';
import KennerSelect from 'components/base/KennerSelect.vue';
import { useResponsive } from 'src/composables/responsive';
import ContentSection from 'components/base/ContentSection.vue'; // adjust to your axios boot file

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
    label: monthNames[m - 1],
    value: m,
  }));
});

// Load all seasons, then filter only those that have at least one league
async function loadSeasonsWithLeagues() {
  loadingSeasons.value = true;
  try {
    const { data: allSeasons } = await api.get<Season[]>('season/seasons');

    // For each season, check if it has leagues
    const leagueResponses = await Promise.all(
      allSeasons.map((s) =>
        api.get<League[]>('league/leagues', { params: { season: s.id } })
      )
    );

    const withLeagues: Season[] = [];
    allSeasons.forEach((season, idx) => {
      if (leagueResponses[idx].data.length > 0) {
        withLeagues.push(season);
      }
    });

    seasonsWithLeagues.value = withLeagues;

    // Preselect the latest (year, month) that actually has leagues
    if (seasonsWithLeagues.value.length > 0) {
      const latest = [...seasonsWithLeagues.value].sort((a, b) => {
        if (a.year !== b.year) return b.year - a.year;
        return b.month - a.month;
      })[0];

      selectedYear.value = latest.year;
      selectedMonth.value = latest.month;
    }
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

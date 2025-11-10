<template>
  <SideAccentBox title="Season Standings" color="teal">
    <q-card flat bordered class="q-pa-md">
      <div class="row items-center q-gutter-md q-mb-md">
        <div class="col">
          <div class="text-h6">Season Standings</div>
        </div>
        <!-- Season (month within selected year) -->
        <div class="row q-gutter-sm items-center">

          <!-- Month -->
          <q-select
            v-if="selectedYear"
            v-model="selectedMonth"
            :options="monthOptions"
            option-label="label"
            option-value="value"
            label="Season"
            dense
            outlined
            emit-value
            map-options
            :disable="!selectedYear || loading"
            @update:model-value="onMonthChange"
            style="min-width: 140px"
          />
          <!-- Year -->
          <q-select
            v-model="selectedYear"
            :options="yearOptions"
            label="Year"
            dense
            outlined
            emit-value
            map-options
            :loading="loadingSeasons"
            :disable="loadingSeasons"
            @update:model-value="onYearChange"
            style="min-width: 140px"
          />


        </div>


      </div>

      <q-banner v-if="error" class="q-mb-md" rounded dense>
        <template #avatar><q-icon name="warning" color="negative" /></template>
        {{ error }}
      </q-banner>

      <div v-if="loading" class="q-pa-xl flex flex-center">
        <q-spinner size="md" color="primary" />
      </div>

      <template v-else>
        <q-banner v-if="!selectedYear" class="q-mb-md" rounded dense>
          <template #avatar><q-icon name="info" /></template>
          Choose a year to continue.
        </q-banner>

        <q-banner v-else-if="!selectedMonth" class="q-mb-md" rounded dense>
          <template #avatar><q-icon name="info" /></template>
          Pick a season in {{ selectedYear }}.
        </q-banner>

        <q-banner v-else-if="leagues.length === 0" class="q-mb-md" rounded dense>
          <template #avatar><q-icon name="info" /></template>
          No leagues found for {{ selectedYear }} · {{ monthLabel(selectedMonth) }}.
        </q-banner>

        <div v-else class="column q-gutter-md">
          <q-card v-for="lg in leagues" :key="lg.id" flat bordered>
            <q-card-section class="row items-center justify-between q-py-sm">
              <div>
                <div class="text-subtitle1">{{ leagueTitle(lg) }}</div>
                <div class="text-caption text-grey-7">
                  League #{{ lg.id }} • {{ selectedYear }} · {{ monthLabel(selectedMonth) }}
                </div>
              </div>
            </q-card-section>

            <q-separator />

            <q-card-section>
              <q-table
                :rows="formatRows(standingsByLeague[lg.id] || [])"
                :columns="columns"
                row-key="rowKey"
                flat
                dense
                hide-bottom
                :pagination="{ rowsPerPage: 10 }"
                :rows-per-page-options="[5, 10, 20, 50]"
              />
              <div v-if="(standingsByLeague[lg.id] || []).length === 0"
                   class="text-caption text-grey-7 q-mt-sm">
                No standings available for this league.
              </div>
            </q-card-section>
          </q-card>
        </div>
      </template>
    </q-card>
  </SideAccentBox>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue';
import { api } from 'boot/axios';
import type { QTableProps } from 'quasar';
import SideAccentBox from 'components/base/SideAccentBox.vue';

/* ---------- Types ---------- */
type Season = { id: number; year: number; month: number; name?: string; title?: string };
type League = { id: number; name?: string; title?: string; season?: number; [k: string]: any };
type LeagueStandingRow = {
  id?: number;
  rank?: number | string;
  player?: string;
  player_profile?: number;
  league_points?: number | string;
  points?: number | string;
  [k: string]: any;
};

/* ---------- State ---------- */
const loadingSeasons = ref(false);
const loading = ref(false);
const error = ref<string | null>(null);

const seasons = ref<Season[]>([]);

const selectedYear = ref<number | null>(null);
const selectedMonth = ref<number | null>(null);
const selectedSeasonId = ref<number | null>(null);

const leagues = ref<League[]>([]);
const standingsByLeague = ref<Record<number, LeagueStandingRow[]>>({});

/* ---------- Helpers ---------- */
const monthNames = [
  '', 'January','February','March','April','May','June',
  'July','August','September','October','November','December'
];

function monthLabel(m?: number | null) {
  if (!m) return '';
  return `S${m} · ${monthNames[m] || m}`;
}
function leagueTitle(lg: League): string {
  return lg.name || lg.title || `League ${lg.id}`;
}
function fmtNum(val: unknown): string {
  if (val === null || val === undefined || val === '') return '';
  const n = Number(val);
  if (!Number.isFinite(n)) return String(val);
  const rounded = Math.round((n + Number.EPSILON) * 1000) / 1000;
  if (Math.trunc(rounded) === rounded) return String(Math.trunc(rounded));
  return String(rounded).replace(/(\.\d*?[1-9])0+$/, '$1').replace(/\.0+$/, '');
}
function cleanPlayerName(name?: string): string {
  return (name || '').replace(/_profile$/i, '');
}

/* ---------- Options ---------- */
const yearOptions = computed(() =>
  Array.from(new Set(seasons.value.map(s => s.year)))
    .sort((a, b) => b - a) // newest first
    .map(y => ({ label: String(y), value: y }))
);

const monthOptions = computed(() => {
  if (!selectedYear.value) return [];
  return seasons.value
    .filter(s => s.year === selectedYear.value)
    .sort((a, b) => a.month - b.month)
    .map(s => ({ label: monthLabel(s.month), value: s.month }));
});

/* ---------- API ---------- */
async function fetchSeasons(): Promise<Season[]> {
  const { data } = await api.get('/season/seasons/');
  return Array.isArray(data) ? data : [];
}
async function fetchLeaguesForSeason(seasonId: number): Promise<League[]> {
  const { data } = await api.get('/league/leagues/', { params: { season: seasonId } });
  return Array.isArray(data) ? data : [];
}
async function fetchLeagueStandings(leagueId: number): Promise<LeagueStandingRow[]> {
  const { data } = await api.get(`/league/leagues/${leagueId}/standings`);
  return Array.isArray(data) ? data : [];
}

/* ---------- Loaders ---------- */
async function loadSeasons() {
  loadingSeasons.value = true;
  error.value = null;
  try {
    seasons.value = await fetchSeasons();
  } catch (e: any) {
    console.error(e);
    error.value = e?.response?.data?.detail || 'Failed to load seasons.';
  } finally {
    loadingSeasons.value = false;
  }
}

function resolveSeasonIdByYearMonth(year: number, month: number): number | null {
  const match = seasons.value.find(s => s.year === year && s.month === month);
  return match ? match.id : null;
}

/* Reset when year changes */
async function onYearChange() {
  selectedMonth.value = null;
  selectedSeasonId.value = null;
  leagues.value = [];
  standingsByLeague.value = {};
  error.value = null;
}

/* Load leagues + standings when month selected */
async function onMonthChange() {
  leagues.value = [];
  standingsByLeague.value = {};
  selectedSeasonId.value = null;
  error.value = null;

  if (!selectedYear.value || !selectedMonth.value) return;

  const sid = resolveSeasonIdByYearMonth(selectedYear.value, selectedMonth.value);
  if (!sid) {
    error.value = 'Season not found for that year/month.';
    return;
  }
  selectedSeasonId.value = sid;

  loading.value = true;
  try {
    const ls = await fetchLeaguesForSeason(sid);
    leagues.value = ls;

    const pairs = await Promise.all(
      ls.map(async (lg) => {
        try {
          const rows = await fetchLeagueStandings(lg.id);
          return [lg.id, rows] as [number, LeagueStandingRow[]];
        } catch {
          return [lg.id, []] as [number, LeagueStandingRow[]];
        }
      })
    );

    const map: Record<number, LeagueStandingRow[]> = {};
    for (const [id, rows] of pairs) map[id] = rows;
    standingsByLeague.value = map;
  } catch (e: any) {
    console.error(e);
    error.value = e?.response?.data?.detail || 'Failed to load leagues/standings.';
  } finally {
    loading.value = false;
  }
}

/* ---------- Table mapping ---------- */
function formatRows(raw: LeagueStandingRow[]) {
  return raw.map((r, idx) => ({
    rowKey: r.id ?? `${idx}-${r.player_profile ?? 'x'}`,
    rank: r.rank ?? null,
    playerName: cleanPlayerName(r.player) || (r.player_profile ? `#${r.player_profile}` : 'Unknown'),
    points: r.points ?? null,
    league_points: r.league_points ?? null,
    ...r,
  }));
}

/* ---------- Columns ---------- */
const columns = computed<QTableProps['columns']>(() => ([
  { name: 'rank', label: 'Rank', field: 'rank', align: 'left', sortable: true, format: (v:any) => fmtNum(v) },
  { name: 'player', label: 'Player', field: 'playerName', align: 'left', sortable: true },
  { name: 'points', label: 'Points', field: 'points', align: 'right', sortable: true, format: (v:any) => fmtNum(v) },
  { name: 'league_points', label: 'League Pts', field: 'league_points', align: 'right', sortable: true, format: (v:any) => fmtNum(v) },
]));

/* ---------- Mount ---------- */
onMounted(async () => {
  await loadSeasons();

  // If something was selected, load its data
  if (selectedYear.value && selectedMonth.value) {
    // ensure monthOptions computed sees selectedYear before month handler runs
    await nextTick();
    await onMonthChange();
  }
});
</script>

<template>
  <q-card flat class="q-pa-md">
    <q-banner v-if="noLeague" class="q-mb-md" rounded dense>
      <template #avatar><q-icon name="info" /></template>
      You are not currently in an active league.
    </q-banner>

    <q-banner v-if="error" class="q-mb-md" rounded dense>
      <template #avatar><q-icon name="warning" color="negative" /></template>
      {{ error }}
    </q-banner>

    <div v-if="loading" class="q-pa-lg flex flex-center">
      <q-spinner size="md" color="primary" />
    </div>

    <template v-else-if="leagueId">
      <q-banner v-if="items.length === 0" rounded dense class="q-mb-md">
        <template #avatar><q-icon name="info" /></template>
        No submitted results found for your league yet.
      </q-banner>

      <div v-else class="column q-gutter-md">
        <q-card v-for="it in items" :key="it.selectedGameId" flat bordered>
          <q-card-section class="row items-center justify-between q-py-sm">
            <div>
              <div class="text-subtitle1">{{ it.title }}</div>
            </div>
          </q-card-section>

          <q-separator />

          <q-card-section>
            <q-table
              :rows="formatRows(it.standings)"
              :columns="columns"
              row-key="rowKey"
              flat
              bordered
              dense
              hide-bottom
              :pagination="{ rowsPerPage: 10 }"
              :rows-per-page-options="[5,10,20,50]"
            />
          </q-card-section>
        </q-card>
      </div>
    </template>
  </q-card>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { api } from 'boot/axios';
import type { QTableProps } from 'quasar';
import { getMyLeagueId } from 'src/services/game/leagueService';

type GameStandingRow = {
  id?: number;
  rank?: number | string;           // may come as number or string
  points?: number | string;         // "12.00"
  league_points?: number | string;  // "6.00"
  player?: string;                  // "haligh_profile"
  player_profile?: number;          // 1
  selected_game?: number;
  [k: string]: any;
};
type SelectedGame = {
  id: number;
  game?: number | { id: number; name?: string };
  game_name?: string;
  created_at?: string;
};

const leagueId = ref<number | null>(null);
const noLeague = computed(() => leagueId.value === null);

const loading = ref(false);
const error = ref<string | null>(null);
const allSelectedGames = ref<SelectedGame[]>([]);
const items = ref<Array<{ selectedGameId: number; title: string; subtitle: string; standings: GameStandingRow[] }>>([]);

/** int unless fractional part present */
function fmtNum(val: unknown): string {
  if (val === null || val === undefined || val === '') return '';
  const n = Number(val);
  if (!Number.isFinite(n)) return String(val);
  const rounded = Math.round((n + Number.EPSILON) * 1000) / 1000;
  if (Math.trunc(rounded) === rounded) return String(Math.trunc(rounded));
  return String(rounded).replace(/(\.\d*?[1-9])0+$/,'$1').replace(/\.0+$/,'');
}

async function fetchSelectedGamesForLeague(lid: number) {
  const { data } = await api.get('/game/selected-games/', { params: { league: lid } });
  return Array.isArray(data) ? (data as SelectedGame[]) : [];
}

async function fetchGameStandings(lid: number, selectedGameId: number) {
  // adjusted url with "leagues"
  const { data } = await api.get(`/league/leagues/${lid}/game-standings`, {
    params: { selected_game: selectedGameId },
  });
  return Array.isArray(data) ? (data as GameStandingRow[]) : [];
}

async function loadData() {
  if (!leagueId.value) return;
  loading.value = true;
  error.value = null;
  items.value = [];
  try {
    allSelectedGames.value = await fetchSelectedGamesForLeague(leagueId.value);

    const checks = await Promise.all(
      allSelectedGames.value.map(async (sg) => {
        try {
          const st = await fetchGameStandings(leagueId.value!, sg.id);
          return { sg, standings: st };
        } catch {
          return { sg, standings: [] as GameStandingRow[] };
        }
      })
    );

    const withResults = checks
      .filter(({ standings }) => standings && standings.length > 0)
      .map(({ sg, standings }) => ({
        selectedGameId: sg.id,
        title: sg.game_name,
        standings,
      }))
      .sort((a, b) => {
        const sa = allSelectedGames.value.find(s => s.id === a.selectedGameId)?.created_at ?? '';
        const sb = allSelectedGames.value.find(s => s.id === b.selectedGameId)?.created_at ?? '';
        return (sb || '').localeCompare(sa || '');
      });

    items.value = withResults;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Failed to load selected games.';
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  try {
    leagueId.value = await getMyLeagueId();
    if (leagueId.value) await loadData();
  } catch (e: any) {
    console.error(e);
    error.value = 'Could not determine your league.';
  }
});

function cleanPlayerName(name?: string): string {
  return (name || '').replace(/_profile$/i, '');
}

function formatRows(raw: GameStandingRow[]) {
  return raw.map((r, idx) => ({
    rowKey: r.id ?? `${idx}-${r.player_profile ?? 'x'}`,
    rank: r.rank ?? null,
    playerName: cleanPlayerName(r.player) || `#${r.player_profile ?? 'unknown'}`,
    points: r.points ?? null,
    league_points: r.league_points ?? null,
    ...r,
  }));
}

/** Columns: show player, points, league points; numbers formatted nicely */
const columns = computed<QTableProps['columns']>(() => ([
  { name: 'rank', label: 'Rank', field: 'rank', align: 'left', sortable: true, format: (v:any) => fmtNum(v) },
  { name: 'player', label: 'Player', field: 'playerName', align: 'left', sortable: true },
  { name: 'points', label: 'Points', field: 'points', align: 'right', sortable: true, format: (v:any) => fmtNum(v) },
  { name: 'league_points', label: 'League Pts', field: 'league_points', align: 'right', sortable: true, format: (v:any) => fmtNum(v) },
]));
</script>

<style scoped>
/* minimal styling */
</style>

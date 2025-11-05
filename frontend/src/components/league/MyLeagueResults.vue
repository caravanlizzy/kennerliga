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

      <!-- Responsive grid (no scrolling) -->
      <div v-else class="row q-col-gutter-md">
        <div
          v-for="it in items"
          :key="it.selectedGameId"
          class="col-12 col-md-6"
        >
          <q-card flat bordered class="result-card">
            <q-card-section
              class="row items-center q-gutter-sm q-py-xs q-pl-sm q-pr-sm"
            >
              <q-icon name="sports_esports" size="18px" class="text-primary" />
              <div class="text-subtitle2 ellipsis">{{ it.title }}</div>
            </q-card-section>

            <q-separator />

            <q-card-section class="q-pt-sm q-pb-sm q-pl-sm q-pr-sm">
              <q-table
                :rows="formatRows(it.standings)"
                :columns="columns"
                row-key="rowKey"
                flat
                wrap-cells
                hide-bottom
                :pagination="{ rowsPerPage: 10 }"
                :rows-per-page-options="[5, 10, 20, 50]"
                table-class="compact-table"
              >
                <!-- Header icons -->
                <template #header-cell-player="props">
                  <q-th :props="props">
                    <q-icon name="person" size="14px" class="q-mr-xs" />
                    Player
                  </q-th>
                </template>
                <template #header-cell-points="props">
                  <q-th :props="props">
                    <q-icon name="score" size="14px" class="q-mr-xs" />
                    Pts
                  </q-th>
                </template>
                <template #header-cell-league_points="props">
                  <q-th :props="props">
                    <q-icon name="military_tech" size="14px" class="q-mr-xs" />
                    LP
                  </q-th>
                </template>

                <!-- Player cell with icon -->
                <template #body-cell-player="props">
                  <q-td :props="props">
                    {{ props.row.playerName }}
                  </q-td>
                </template>

                <!-- Points cell with medals / last-place face -->
                <template #body-cell-points="props">
                  <q-td :props="props" class="no-wrap">
                    <!-- top 3 medals -->
                    <q-icon
                      v-if="props.row.rankNum === 1"
                      name="emoji_events"
                      size="14px"
                      class="q-mr-xs text-amber-7"
                    />
                    <q-icon
                      v-else-if="props.row.rankNum === 2"
                      name="emoji_events"
                      size="14px"
                      class="q-mr-xs text-blue-grey-5"
                    />
                    <q-icon
                      v-else-if="props.row.rankNum === 3"
                      name="emoji_events"
                      size="14px"
                      class="q-mr-xs text-deep-orange-5"
                    />
                    <!-- fun loser icon for last place -->
                    <q-icon
                      v-else-if="props.row.isLast"
                      name="sentiment_very_dissatisfied"
                      size="14px"
                      class="q-mr-xs text-negative"
                    />
                    {{ fmtNum(props.row.points) }}
                  </q-td>
                </template>
              </q-table>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </template>
  </q-card>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { api } from 'boot/axios';
import type { QTableProps } from 'quasar';

import { getMyLeagueId } from 'src/services/leagueService';

type GameStandingRow = {
  id?: number;
  rank?: number | string;
  points?: number | string;
  league_points?: number | string;
  player?: string;
  player_profile?: number;
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
const items = ref<
  Array<{ selectedGameId: number; title: string; standings: GameStandingRow[] }>
>([]);

function fmtNum(val: unknown): string {
  if (val === null || val === undefined || val === '') return '';
  const n = Number(val);
  if (!Number.isFinite(n)) return String(val);
  const rounded = Math.round((n + Number.EPSILON) * 1000) / 1000;
  if (Math.trunc(rounded) === rounded) return String(Math.trunc(rounded));
  return String(rounded)
    .replace(/(\.\d*?[1-9])0+$/, '$1')
    .replace(/\.0+$/, '');
}

async function fetchSelectedGamesForLeague(lid: number) {
  const { data } = await api.get('/game/selected-games/', {
    params: { league: lid },
  });
  return Array.isArray(data) ? (data as SelectedGame[]) : [];
}

async function fetchGameStandings(lid: number, selectedGameId: number) {
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
        const sa =
          allSelectedGames.value.find((s) => s.id === a.selectedGameId)
            ?.created_at ?? '';
        const sb =
          allSelectedGames.value.find((s) => s.id === b.selectedGameId)
            ?.created_at ?? '';
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

/** Build rows with rank awareness so we can mark the last place for the icon. */
function formatRows(raw: GameStandingRow[]) {
  // compute last rank among numeric ranks in this table
  const rankNums = raw
    .map((r) => Number(r.rank))
    .filter((n) => Number.isFinite(n)) as number[];
  const lastRank = rankNums.length ? Math.max(...rankNums) : null;

  return raw.map((r, idx) => {
    const rankNum = Number(r.rank);
    const validRank = Number.isFinite(rankNum) ? rankNum : null;

    return {
      rowKey: r.id ?? `${idx}-${r.player_profile ?? 'x'}`,
      rankNum: validRank, // keep numeric rank (hidden)
      isLast: lastRank !== null && validRank === lastRank,
      playerName:
        cleanPlayerName(r.player) || `#${r.player_profile ?? 'unknown'}`,
      points: r.points ?? null,
      league_points: r.league_points ?? null,
      ...r,
    };
  });
}

/** Columns (no Rank column shown) */
const columns = computed<QTableProps['columns']>(() => [
  {
    name: 'player',
    label: 'Player',
    field: 'playerName',
    align: 'left',
    sortable: true,
  },
  {
    name: 'points',
    label: 'Pts',
    field: 'points',
    align: 'right',
    sortable: true,
    format: (v: any) => fmtNum(v),
  },
  {
    name: 'league_points',
    label: 'LP',
    field: 'league_points',
    align: 'right',
    sortable: true,
    format: (v: any) => fmtNum(v),
  },
]);
</script>

<style scoped>
.result-card {
  border-radius: 10px;
  --q-card-padding: 0;
}

/* Allow wrapping so tables fit without scrolling */
:deep(.q-table__grid-content),
:deep(.q-table tbody td),
:deep(.q-table thead th) {
  white-space: normal !important;
  word-break: break-word;
}

.no-wrap {
  white-space: nowrap;
}

.ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>

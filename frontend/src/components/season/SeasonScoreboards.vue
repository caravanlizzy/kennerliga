<template>
  <div v-if="seasonData">
    <div class="text-h5">{{ seasonData.season.name }}</div>

    <div v-for="league in sortedLeagues" :key="league.league.id">
      <div>L{{ league.league.level }}</div>

      <q-table
        :columns="toQTable(league).columns"
        :rows="toQTable(league).rows"
        row-key="__key"
        flat
        bordered
        dense
        hide-bottom
        separator="cell"
      >
        <template #body="props">
          <q-tr
            :props="props"
            :class="props.row.__key === 'totals' ? 'totals-row' : ''"
          >
            <q-td v-for="col in props.cols" :key="col.name" :props="props">
              {{ props.row[col.name] }}
            </q-td>
          </q-tr>
        </template>
      </q-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { api } from 'boot/axios';

interface ScoreCell {
  player_id: number;
  profile_name: string;
  value: number | null;
  display: string;
}
interface ScoreRow {
  type: 'game' | 'league_totals';
  game?: string;
  label?: string;
  cells: ScoreCell[];
}
interface LeagueScoreboard {
  league: { id: number; level: number };
  columns: string[];
  rows: ScoreRow[];
}
interface SeasonScoreboardsResponse {
  season: { id: number; name: string };
  leagues: LeagueScoreboard[];
}

const props = defineProps<{ seasonId: number | null }>();
const seasonData = ref<SeasonScoreboardsResponse | null>(null);

const sortedLeagues = computed(() =>
  seasonData.value?.leagues
    ? [...seasonData.value.leagues].sort(
        (a, b) => a.league.level - b.league.level
      )
    : []
);

watch(
  () => props.seasonId,
  async (id) => {
    if (id == null) return;
    const { data } = await api(`season/season-scoreboards/${id}/scoreboards/`);
    seasonData.value = data;

    // If backend not ready, keep or replace with your mock here:
    seasonData.value = {
      season: { id: 34, name: '2025_S10' },
      leagues: [
        {
          league: { id: 101, level: 1 },
          columns: ['Game', 'Alice', 'Bob'],
          rows: [
            {
              type: 'game',
              selected_game_id: 1001,
              game: 'Catan',
              cells: [
                {
                  player_id: 1,
                  profile_name: 'Alice',
                  value: 83,
                  display: '83 pts',
                },
                {
                  player_id: 2,
                  profile_name: 'Bob',
                  value: 75,
                  display: '75 pts',
                },
              ],
            },
            {
              type: 'league_totals',
              label: 'League Points',
              cells: [
                {
                  player_id: 1,
                  profile_name: 'Alice',
                  value: 3,
                  display: '3 pts',
                },
                {
                  player_id: 2,
                  profile_name: 'Bob',
                  value: 1,
                  display: '1 pts',
                },
              ],
            },
          ],
        },
      ],
    };
  },
  { immediate: true }
);

/**
 * Convert one league’s payload to QTable columns & rows
 * Keys: 'game' then 'c0','c1',... for each player column.
 */
function toQTable(league: LeagueScoreboard) {
  // columns
  const columns = league.columns.map((label, i) => {
    if (i === 0) {
      return { name: 'game', label, field: 'game', align: 'left' as const };
    }
    const key = `c${i - 1}`;
    return { name: key, label, field: key, align: 'left' as const };
  });

  // rows: all game rows + (optional) totals as last row
  const gameRows = league.rows
    .filter((r) => r.type === 'game')
    .map((r, idx) => {
      const row: Record<string, any> = {
        __key: `g-${idx}`,
        game: r.game ?? '',
      };
      r.cells.forEach((cell, i) => {
        row[`c${i}`] = cell.display;
      });
      return row;
    });

  const totals = league.rows.find((r) => r.type === 'league_totals');
  const totalsRow = totals
    ? (() => {
        const row: Record<string, any> = {
          __key: 'totals',
          game: totals.label ?? 'Totals',
        };
        totals.cells.forEach((cell, i) => {
          row[`c${i}`] = cell.display;
        });
        return row;
      })()
    : null;

  const rows = totalsRow ? [...gameRows, totalsRow] : gameRows;
  return { columns, rows };
}
</script>

<style scoped>
.q-table tbody tr.totals-row td {
  border-top: 1px solid currentColor !important; /* thick horizontal rule */
}
</style>

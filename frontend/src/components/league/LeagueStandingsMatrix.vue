<template>
  <div class="full-width">
    <q-table
      v-if="standings"
      :rows="tableRows"
      :columns="tableColumns"
      row-key="player_profile_id"
      flat
      bordered
      hide-pagination
      :pagination="{ rowsPerPage: 0 }"
      class="standings-table"
      table-header-class="bg-primary text-white"
    >
      <template #body-cell-profile_name="props">
        <q-td :props="props" class="text-weight-medium">
          <q-icon
            v-if="props.rowIndex === 0"
            name="emoji_events"
            class="q-mr-xs"
            color="amber"
            size="sm"
          />
          <q-icon
            v-else-if="props.rowIndex === tableRows.length - 1"
            name="img:https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/1f422.png"
            class="q-mr-xs"
            size="xs"
          />
          <q-icon v-else name="person" class="q-mr-xs" color="primary" size="xs" />
          {{ props.value }}
        </q-td>
      </template>

      <template #body-cell-total="props">
        <q-td :props="props" class="bg-grey-2">
          <q-badge color="primary" class="text-subtitle2 q-pa-sm" rounded>
            {{ props.value }}
          </q-badge>
        </q-td>
      </template>

      <template #body-cell="props">
        <q-td :props="props" v-if="props.col.name !== 'profile_name' && props.col.name !== 'total'">
          <div v-if="props.value" class="column items-center q-gutter-xs">
            <q-chip
              dense
              color="positive"
              text-color="white"
              size="sm"
              class="q-ma-none"
            >
              {{ formatNumber(props.value.league_points) }} LP
            </q-chip>
            <span class="text-caption text-grey-7">
              {{ formatNumber(props.value.points) }} pts
            </span>
          </div>
          <div v-else class="column items-center text-grey-5">
            <q-icon name="remove" size="sm" />
          </div>
        </q-td>
      </template>
    </q-table>

    <!-- Loading State -->
    <div v-else-if="loading" class="column items-center justify-center q-pa-xl">
      <q-spinner-dots color="primary" size="40px" />
      <span class="text-grey-7 q-mt-md">Loading standings...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="column items-center justify-center q-pa-xl">
      <q-icon name="error_outline" color="negative" size="48px" />
      <span class="text-negative q-mt-md text-subtitle1">Error loading standings</span>
      <q-btn
        flat
        color="primary"
        label="Retry"
        class="q-mt-sm"
        @click="fetchStandings"
      />
    </div>
  </div>
</template>


<script setup lang="ts">
import { ref, computed } from 'vue';
import { api } from 'boot/axios';
import type { QTableColumn } from 'quasar';

interface GameStats {
  points: string;
  league_points: string;
  rank: number;
}

interface Standing {
  player_profile_id: number;
  profile_name: string;
  total_league_points: string;
  total_wins: string;
  games: Record<string, GameStats>;
}

interface SelectedGame {
  id: number;
  game_name: string;
}

interface StandingsData {
  selected_games: SelectedGame[];
  standings: Standing[];
}

const standings = ref<StandingsData | null>(null);
const loading = ref(true);
const error = ref(false);

try {
  const { data } = await api.get<StandingsData>('league/leagues/1/full-standings/');
  standings.value = data;
} catch (e) {
  console.error('Error fetching standings:', e);
  error.value = true;
} finally {
  loading.value = false;
}

const tableColumns = computed<QTableColumn[]>(() => {
  if (!standings.value) return [];

  const columns: QTableColumn[] = [
    {
      name: 'profile_name',
      label: 'Player',
      field: 'profile_name',
      align: 'left',
      sortable: true,
    },
  ];

  // Add a column for each game
  standings.value.selected_games.forEach((game) => {
    columns.push({
      name: `game_${game.id}`,
      label: game.game_name,
      field: `game_${game.id}`,
      align: 'center',
    });
  });

  // Add total column
  columns.push({
    name: 'total',
    label: 'Total LP',
    field: 'total_league_points',
    align: 'center',
    sortable: true,
  });

  return columns;
});

const tableRows = computed(() => {
  if (!standings.value) return [];

  return standings.value.standings.map((standing) => {
    const row: Record<string, unknown> = {
      player_profile_id: standing.player_profile_id,
      profile_name: standing.profile_name,
      total_league_points: standing.total_league_points,
    };

    // Add game data
    standings.value!.selected_games.forEach((game) => {
      const gameData = standing.games[game.id.toString()];
      row[`game_${game.id}`] = gameData || null;
    });

    return row;
  });
});

const formatNumber = (value: string | number): string => {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '-';
  return num % 1 === 0 ? num.toFixed(0) : num.toString();
};
</script>


<style lang="scss" scoped>
.standings-table {
  :deep(th) {
    font-weight: 600;
    font-size: 0.9rem;
  }

  :deep(tbody tr:hover) {
    background-color: rgba(var(--q-primary-rgb), 0.05);
  }

  :deep(td) {
    vertical-align: middle;
  }
}
</style>

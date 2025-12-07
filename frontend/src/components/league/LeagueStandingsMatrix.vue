
<template>
  <div class="full-width">
    <q-table
      v-if="standings"
      :rows="tableRows"
      :columns="tableColumns"
      row-key="player_profile_id"
      flat
      hide-pagination
      :pagination="{ rowsPerPage: 0 }"
      class="standings-table"
    >
      <!-- Header cells -->
      <template #header="props">
        <q-tr :props="props" class="standings-header">
          <q-th
            v-for="col in props.cols"
            :key="col.name"
            :props="props"
            class="standings-header-cell"
          >
            {{ col.label }}
          </q-th>
        </q-tr>
      </template>

      <!-- Player name column -->
      <template #body-cell-profile_name="props">
        <q-td :props="props" class="player-cell">
          <div class="row items-center no-wrap">
            <div
              v-if="props.rowIndex === 0"
              class="rank-badge rank-gold"
            >
              <q-icon name="emoji_events" size="16px" />
            </div>
            <div
              v-else-if="props.rowIndex === 1"
              class="rank-badge rank-silver"
            >
              2
            </div>
            <div
              v-else-if="props.rowIndex === 2"
              class="rank-badge rank-bronze"
            >
              3
            </div>
            <div
              v-else-if="props.rowIndex === tableRows.length - 1"
              class="rank-badge rank-last"
            >
              <q-icon
                name="img:https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/1f422.png"
                size="14px"
              />
            </div>
            <div v-else class="rank-badge rank-default">
              {{ props.rowIndex + 1 }}
            </div>
            <span class="player-name">{{ props.value }}</span>
          </div>
        </q-td>
      </template>

      <!-- Total column -->
      <template #body-cell-total="props">
        <q-td :props="props" class="total-cell">
          <div class="total-value">
            {{ props.value }}
          </div>
        </q-td>
      </template>

      <!-- Game columns -->
      <template #body-cell="props">
        <q-td
          :props="props"
          v-if="props.col.name !== 'profile_name' && props.col.name !== 'total'"
          class="game-cell"
        >
          <div v-if="props.value" class="game-stats">
            <span class="lp-value">{{ formatNumber(props.value.league_points) }}</span>
            <span class="pts-value">{{ formatNumber(props.value.points) }} pts</span>
          </div>
          <div v-else class="no-data">
            <span class="dot"></span>
          </div>
        </q-td>
      </template>
    </q-table>

    <!-- Loading State -->
    <div v-else-if="loading" class="state-container">
      <div class="state-card">
        <q-spinner-dots color="primary" size="32px" />
        <span class="state-text">Loading standings...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="state-container">
      <div class="state-card state-error">
        <q-icon name="error_outline" size="32px" class="text-negative" />
        <span class="state-text text-negative">Error loading standings</span>
        <q-btn
          outline
          color="primary"
          label="Retry"
          size="sm"
          class="q-mt-md"
          @click="fetchStandings"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { api } from 'boot/axios';
import type { QTableColumn } from 'quasar';

const props = defineProps<{leagueId: number}>();

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

const fetchStandings = async () => {
  loading.value = true;
  error.value = false;
  try {
    const { data } = await api.get<StandingsData>(`league/leagues/${props.leagueId}/full-standings/`);
    standings.value = data;
  } catch (e) {
    console.error('Error fetching standings:', e);
    error.value = true;
  } finally {
    loading.value = false;
  }
};

// Initial fetch
fetchStandings();

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
  background: white;
  border: 1px dotted rgba(0, 0, 0, 0.12);
  border-radius: 12px;
  overflow: hidden;

  :deep(.q-table) {
    border-spacing: 0;
  }

  :deep(thead),
  :deep(tbody),
  :deep(tr),
  :deep(th),
  :deep(td) {
    border: none;
  }
}

.standings-header {
  background: white;
}

.standings-header-cell {
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #9e9e9e;
  padding: 16px 12px;
  border-bottom: 1px dotted rgba(0, 0, 0, 0.12) !important;
}

.player-cell {
  padding: 12px;
  border-bottom: 1px dotted rgba(0, 0, 0, 0.06);
}

.player-name {
  font-weight: 500;
  color: #424242;
  margin-left: 12px;
}

.rank-badge {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.rank-gold {
  background: linear-gradient(135deg, #ffd700 0%, #ffb300 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(255, 179, 0, 0.3);
}

.rank-silver {
  background: linear-gradient(135deg, #e0e0e0 0%, #bdbdbd 100%);
  color: white;
}

.rank-bronze {
  background: linear-gradient(135deg, #d7a574 0%, #cd7f32 100%);
  color: white;
}

.rank-last {
  background: #f5f5f5;
  border: 1px dotted #e0e0e0;
}

.rank-default {
  background: #fafafa;
  color: #9e9e9e;
  border: 1px dotted #e0e0e0;
}

.game-cell {
  padding: 12px 8px;
  border-bottom: 1px dotted rgba(0, 0, 0, 0.06);
  border-left: 1px dotted rgba(0, 0, 0, 0.06);
}

.game-stats {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.lp-value {
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--q-primary);
}

.pts-value {
  font-size: 0.7rem;
  color: #9e9e9e;
}

.no-data {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.no-data .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #e0e0e0;
}

.total-cell {
  padding: 12px;
  border-bottom: 1px dotted rgba(0, 0, 0, 0.06);
  border-left: 1px dotted rgba(0, 0, 0, 0.06);
  background: #fafafa;
}

.total-value {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--q-primary);
  text-align: center;
}

// Hover effect
:deep(tbody tr:hover) {
  background-color: #fafafa;
}

// First row highlight for leader
:deep(tbody tr:first-child) {
  background: linear-gradient(90deg, rgba(255, 215, 0, 0.05) 0%, transparent 100%);
}

// State containers
.state-container {
  display: flex;
  justify-content: center;
  padding: 48px 24px;
}

.state-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 48px;
  background: white;
  border: 1px dotted rgba(0, 0, 0, 0.12);
  border-radius: 12px;
}

.state-text {
  margin-top: 12px;
  font-size: 0.9rem;
  color: #757575;
}

.state-error .state-text {
  color: var(--q-negative);
}
</style>

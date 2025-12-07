<template>
  <div class="standings-root">
    <div class="standings-header-bar">
      <div class="standings-title">Standings</div>
      <q-badge
        v-if="leagueLevel"
        color="primary"
        text-color="white"
        class="league-badge"
      >
        L{{ leagueLevel }}
      </q-badge>
    </div>

    <div class="standings-table-wrapper">
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
              <span class="lp-value">
                {{ formatNumber(props.value.league_points) }}
              </span>
              <span class="pts-value">
                {{ formatNumber(props.value.points) }} pts
              </span>
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
          <q-spinner-dots size="24px" />
          <span class="state-text">Loading standings...</span>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="state-container">
        <div class="state-card state-error">
          <q-icon name="error_outline" size="24px" class="text-negative" />
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { api } from 'boot/axios';
import type { QTableColumn } from 'quasar';

const props = defineProps<{
  leagueId: number;
  leagueLevel?: number; // pass league.level from parent
}>();

const leagueLevel = computed(() => props.leagueLevel ?? null);

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
    const { data } = await api.get<StandingsData>(
      `league/leagues/${props.leagueId}/full-standings/`
    );
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

  standings.value.selected_games.forEach((game) => {
    columns.push({
      name: `game_${game.id}`,
      label: game.game_name,
      field: `game_${game.id}`,
      align: 'center',
    });
  });

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
.standings-root {
  max-width: 100%;
}

/* Header bar with badge */
.standings-header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.standings-title {
  font-size: 0.9rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #616161;
}

.league-badge {
  font-weight: 600;
  border-radius: 999px;
  padding: 2px 10px;
  font-size: 0.75rem;
}

/* Wrapper to allow horizontal scroll on small screens */
.standings-table-wrapper {
  background: #f9f9f9;
  padding: 4px;
  overflow-x: auto;
}

/* Compact table */
.standings-table {
  background: #fdfdfd;
  border-radius: 8px;
  font-size: 0.8rem;

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

  /* Make table not shrink columns too much,
     enable scrolling instead on very narrow screens */
  :deep(.q-table__middle) {
    min-width: 560px;
  }
}

.standings-header {
  background: #f3f3f3;
}

.standings-header-cell {
  font-weight: 600;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #757575;
  padding: 8px 8px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08) !important;
}

.player-cell {
  padding: 8px 8px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.player-name {
  font-weight: 500;
  color: #424242;
  margin-left: 8px;
  font-size: 0.85rem;
}

.rank-badge {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}

.rank-gold {
  background: linear-gradient(135deg, #ffd700 0%, #ffb300 100%);
  color: white;
  box-shadow: 0 1px 4px rgba(255, 179, 0, 0.4);
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
  border: 1px solid #e0e0e0;
}

.rank-default {
  background: #fafafa;
  color: #9e9e9e;
  border: 1px solid #e0e0e0;
}

.game-cell {
  padding: 8px 6px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
  border-left: 1px solid rgba(0, 0, 0, 0.04);
}

.game-stats {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
}

.lp-value {
  font-weight: 600;
  font-size: 0.82rem;
  color: var(--q-primary);
}

.pts-value {
  font-size: 0.68rem;
  color: #9e9e9e;
}

.no-data {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.no-data .dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #d6d6d6;
}

.total-cell {
  padding: 8px 6px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
  border-left: 1px solid rgba(0, 0, 0, 0.04);
  background: #f5f5f5;
}

.total-value {
  font-weight: 700;
  font-size: 0.9rem;
  color: var(--q-primary);
  text-align: center;
}

/* Hover row */
:deep(tbody tr:hover) {
  background-color: #f5f5f5;
}

/* Leading row subtle highlight */
:deep(tbody tr:first-child) {
  background: linear-gradient(
      90deg,
      rgba(255, 215, 0, 0.03) 0%,
      transparent 100%
  );
}

/* State containers */
.state-container {
  display: flex;
  justify-content: center;
  padding: 24px 12px;
}

.state-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 28px;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 10px;
}

.state-text {
  margin-top: 8px;
  font-size: 0.8rem;
  color: #757575;
}

.state-error .state-text {
  color: var(--q-negative);
}
</style>

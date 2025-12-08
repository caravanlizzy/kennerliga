<template>
  <div>
    <!-- Optional league badge (no 'Standings' text) -->
    <div class="row items-center justify-end">
      <q-badge
        v-if="leagueLevel"
        color="primary"
        text-color="white"
        class="q-px-sm q-py-xs text-caption text-weight-bold"
        rounded
      >
        L{{ leagueLevel }}
      </q-badge>
    </div>

    <!-- Table / states -->
    <div class="overflow-auto">
      <q-table
        v-if="standings"
        :rows="tableRows"
        :columns="tableColumns"
        row-key="player_profile_id"
        flat
        dense
        hide-pagination
        :pagination="{ rowsPerPage: 0 }"
        :row-class="rowClass"
        class="bg-white rounded-borders text-caption"
      >
        <!-- Header cells (very minimal styling) -->
        <template #header="props">
          <q-tr :props="props">
            <q-th
              v-for="col in props.cols"
              :key="col.name"
              :props="props"
              :class="[
                'q-px-xs q-py-xs text-uppercase text-weight-medium',
                col.name === 'profile_name' ? 'text-left' : 'text-center',
              ]"
              :style="
                col.name.startsWith('game_')
                  ? 'max-width: 90px; white-space: normal; line-height: 1.15;'
                  : ''
              "
            >
              {{ col.label }}
            </q-th>
          </q-tr>
        </template>

        <!-- Player name column -->
        <template #body-cell-profile_name="props">
          <q-td
            :props="props"
            class="q-px-xs q-py-xs text-left text-body2 text-weight-medium"
          >
            <div class="row items-center no-wrap">
              <span>{{ props.value }}</span>
            </div>
          </q-td>
        </template>

        <!-- Total column -->
        <template #body-cell-total="props">
          <q-td :props="props" class="q-px-xs q-py-xs text-center">
            <div class="text-primary text-weight-bold text-body2">
              {{ formatNumber(props.value) }}
            </div>
          </q-td>
        </template>

        <!-- All game columns -->
        <template #body-cell="props">
          <q-td
            v-if="
              props.col.name !== 'profile_name' && props.col.name !== 'total'
            "
            :props="props"
            class="q-px-xs q-py-xs text-center"
          >
            <div
              v-if="
                props.value && (props.value.points || props.value.league_points)
              "
              class="column items-center"
            >
              <span v-if="props.value.points" class="text-caption">
                {{ formatNumber(props.value.points) }} VP
              </span>
              <div
                v-if="props.value.league_points"
		class="text-grey-8 floating"
              >
                {{ formatNumber(props.value.league_points) }}
              </div>

            </div>
            <div v-else class="flex flex-center">
              <q-icon name="circle" size="6px" color="grey-4" />
            </div>
          </q-td>
        </template>
      </q-table>

      <!-- Loading state -->
      <div
        v-else-if="loading"
        class="column items-center q-pa-md bg-white rounded-borders"
      >
        <q-spinner-dots size="24px" />
        <span class="q-mt-xs text-caption"> Loading standings... </span>
      </div>

      <!-- Error state -->
      <div
        v-else-if="error"
        class="column items-center q-pa-md bg-white rounded-borders"
      >
        <q-icon name="error_outline" size="24px" color="negative" />
        <span class="q-mt-xs text-negative text-caption">
          Error loading standings
        </span>
        <q-btn
          outline
          color="primary"
          label="Retry"
          size="sm"
          class="q-mt-sm"
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
import { useResponsive } from 'src/composables/reponsive';

const props = defineProps<{
  leagueId: number;
  leagueLevel?: number;
}>();

const leagueLevel = computed(() => props.leagueLevel ?? null);
const { isMobile } = useResponsive();

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
  game_short_name: string; // 🔹 now available
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

// initial load
fetchStandings();

const tableColumns = computed<QTableColumn[]>(() => {
  if (!standings.value) return [];

  const cols: QTableColumn[] = [
    {
      name: 'profile_name',
      label: 'Player',
      field: 'profile_name',
      align: 'left',
      sortable: true,
    },
  ];

  standings.value.selected_games.forEach((game) => {
    cols.push({
      name: `game_${game.id}`,
      // 🔹 short name on mobile, full name otherwise
      label: (isMobile && game.game_short_name) ? game.game_short_name : game.game_name,
      field: `game_${game.id}`,
      align: 'center',
    });
  });

  cols.push({
    name: 'total',
    label: 'Total LP',
    field: 'total',
    align: 'center',
    sortable: true,
  });

  return cols;
});

const tableRows = computed(() => {
  if (!standings.value) return [];

  return standings.value.standings.map((standing) => {
    const row: Record<string, unknown> = {
      player_profile_id: standing.player_profile_id,
      profile_name: standing.profile_name,
      total: standing.total_league_points,
    };

    standings.value!.selected_games.forEach((game) => {
      const gameData = standing.games[game.id.toString()];
      row[`game_${game.id}`] = gameData || null;
    });

    return row;
  });
});

// highlight winner row (first row) gently
const rowClass = (_row: unknown, index: number) =>
  index === 0 ? 'bg-yellow-1' : '';

const formatNumber = (value: string | number): string => {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if ((num as number) === 0) return '0';
  if (!num) return '-';
  return (num as number) % 1 === 0 ? (num as number).toFixed(0) : String(num);
};
</script>

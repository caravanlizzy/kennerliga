<template>
  <div>
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
                'text-uppercase text-weight-medium',
                col.name === 'profile_name' ? 'text-left' : 'text-center',
              ]"
              :style="
                col.name.startsWith('game_')
                  ? 'max-width: 80px; white-space: normal; line-height: 1.1; padding: 4px 8px;'
                  : 'padding: 4px 8px;'
              "
            >
              {{ col.label }}
            </q-th>
          </q-tr>
        </template>

        <template #body-cell-profile_name="props">
          <q-td :props="props" class="text-left" style="padding: 4px 8px">
            <div class="row items-center no-wrap">
              <template v-if="props.row.username">
                <div class="row items-center no-wrap q-gutter-x-sm">
                  <UserAvatar
                    :display-username="props.row.username"
                    size="24px"
                  />
                  <div class="column">
                    <span class="text-weight-bold">{{
                      props.row.username
                    }}</span>
                    <span
                      v-if="!isMobile && props.row.profile_name"
                      class="text-caption text-grey-7"
                      style="font-size: 0.7rem; line-height: 1"
                    >
                      {{ props.row.profile_name }}
                    </span>
                  </div>
                </div>
              </template>
              <template v-else>
                <template v-if="isMobile">
                  <q-badge
                    color="grey-3"
                    text-color="grey-9"
                    class="text-weight-bold"
                  >
                    {{ props.value.substring(0, 3).toUpperCase() }}
                    <q-tooltip>
                      {{ props.value }}
                    </q-tooltip>
                  </q-badge>
                </template>
                <template v-else>
                  <span class="text-weight-bold">{{ props.value }}</span>
                </template>
              </template>

              <!-- League Leader Celebration (First Row) -->
              <q-icon
                v-if="props.rowIndex === 0"
                name="emoji_events"
                color="amber-8"
                size="xs"
                class="q-ml-xs"
              >
                <q-tooltip>League Leader</q-tooltip>
              </q-icon>
            </div>
          </q-td>
        </template>

        <!-- Total column -->
        <template #body-cell-total="props">
          <q-td :props="props" class="text-right" style="padding: 4px 8px">
            <div class="text-dark text-weight-bold text-caption">
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
            class="q-px-xs q-py-xs text-center relative-position overflow-hidden"
            style="padding: 4px 6px"
            :class="getRankBgClass(props.value?.rank)"
          >
            <!-- Rank Indicator Bar -->
            <div
              v-if="props.value?.rank && props.value.rank <= 4"
              class="rank-indicator"
              :class="getRankIndicatorClass(props.value.rank)"
            ></div>

            <div
              v-if="
                props.value && (props.value.points || props.value.league_points)
              "
              class="column items-center"
              style="line-height: 1.1"
            >
              <div
                v-if="props.value.points"
                class="text-weight-bold text-dark row items-baseline"
                style="font-size: 0.9rem"
              >
                <span>{{ displayPointsValue(props.value.points) }}</span>
                <span
                  v-if="!isRank(props.value.points)"
                  class="text-weight-medium q-ml-xs"
                  style="font-size: 0.6rem; opacity: 0.7"
                  >VP</span
                >
              </div>
              <div
                v-if="props.value.league_points"
                class="text-grey-6 text-weight-medium"
                style="font-size: 0.65rem"
              >
                {{ formatNumber(props.value.league_points)
                }}<span
                  style="font-size: 0.55rem; margin-left: 1px; opacity: 0.8"
                  >LP</span
                >
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
          color="dark"
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
import { useResponsive } from 'src/composables/responsive';
import UserAvatar from 'components/ui/UserAvatar.vue';

const props = defineProps<{
  leagueId: number;
}>();

const { isMobile } = useResponsive();

interface GameStats {
  points: string;
  league_points: string;
  rank: number;
}

interface Standing {
  player_profile_id: number;
  profile_name: string;
  username?: string;
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
      label: '',
      field: 'profile_name',
      align: 'left',
      sortable: true,
    },
  ];

  standings.value.selected_games.forEach((game) => {
    cols.push({
      name: `game_${game.id}`,
      // 🔹 short name on mobile, full name otherwise
      label:
        isMobile && game.game_short_name
          ? game.game_short_name
          : game.game_name,
      field: `game_${game.id}`,
      align: 'center',
    });
  });

  cols.push({
    name: 'total',
    label: 'LP',
    field: 'total',
    align: 'right',
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
      username: standing.username,
      total: standing.total_league_points,
    };

    standings.value.selected_games.forEach((game) => {
      const gameData = standing.games[game.id.toString()];
      row[`game_${game.id}`] = gameData || null;
    });

    return row;
  });
});

// highlight winner row (first row) gently
const rowClass = (_row: unknown, index: number) =>
  index === 0 ? 'bg-orange-1 league-leader-row' : '';

const formatNumber = (value: string | number): string => {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if ((num as number) === 0) return '0';
  if (!num) return '-';
  return (num as number) % 1 === 0 ? (num as number).toFixed(0) : String(num);
};

function isRank(points: string) {
  return ['-1.00', '-2.00', '-3.00', '-4.00'].includes(points);
}

function displayPointsValue(points: string) {
  switch (points) {
    case '-1.00':
      return '1st';
    case '-2.00':
      return '2nd';
    case '-3.00':
      return '3rd';
    case '-4.00':
      return '4th';
    default:
      return formatNumber(points);
  }
}

function getRankBgClass(rank: number | undefined) {
  if (!rank) return '';
  switch (rank) {
    case 1:
      return 'bg-amber-1';
    case 2:
      return 'bg-blue-grey-1';
    case 3:
      return 'bg-brown-1';
    default:
      return '';
  }
}

function getRankIndicatorClass(rank: number) {
  switch (rank) {
    case 1:
      return 'bg-amber-6';
    case 2:
      return 'bg-blue-grey-4';
    case 3:
      return 'bg-brown-4';
    case 4:
      return 'bg-red-4';
    default:
      return '';
  }
}
</script>

<style scoped lang="scss">
.rank-indicator {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 3px;
}

.league-leader-row {
  border-left: 3px solid var(--q-amber-7) !important;
}

/* Ensure the background doesn't override the hover effect of q-table if any */
:deep(.q-table tbody tr:hover) td.bg-amber-1,
:deep(.q-table tbody tr:hover) td.bg-blue-grey-1,
:deep(.q-table tbody tr:hover) td.bg-brown-1,
:deep(.q-table tbody tr.bg-orange-1:hover) {
  filter: brightness(0.95);
}
</style>

<template>
  <div>
    <!-- Table / states -->
    <div class="overflow-auto">
      <q-table
        v-if="standings && (standings.standings.length > 0 || (standings.selected_games && standings.selected_games.length > 0))"
        :rows="tableRows"
        :columns="tableColumns"
        row-key="player_profile_id"
        flat
        dense
        hide-pagination
        :pagination="{ rowsPerPage: 0 }"
        :row-class="rowClass"
        class="bg-standings-table rounded-borders text-caption"
      >
        <template #no-data>
          <!-- This slot will not be used because of v-if above, but good practice -->
          <div class="hidden"></div>
        </template>
        <template #header="props">
          <q-tr :props="props" class="header-row">
            <q-th
              v-for="col in props.cols"
              :key="col.name"
              :props="props"
              :class="[
                'text-uppercase text-weight-bold text-grey-8',
                col.name === 'profile_name' ? 'text-left' : 'text-center',
              ]"
              :style="
                col.name.startsWith('game_')
                  ? 'max-width: 90px; white-space: normal; line-height: 1.2; padding: 12px 8px;'
                  : 'padding: 12px 8px;'
              "
            >
              <div v-if="col.name === 'total'" class="row items-center justify-end q-gutter-x-xs">
                 <q-icon name="stars" color="primary" size="14px" />
                 <span>{{ col.label }}</span>
              </div>
              <div v-else-if="col.name.startsWith('game_')" class="column items-center">
                <span>{{ col.label }}</span>
                <div v-if="(col as any).platformName" class="text-grey-7 text-weight-medium" style="font-size: 0.55rem; line-height: 1; margin-top: 1px;">
                  {{ (col as any).platformName }}
                </div>
                <div v-if="(col as any).selectedByName" class="text-grey-6" style="font-size: 0.6rem; font-weight: normal; margin-top: 2px;">
                  <span class="text-grey-5">by </span>{{ (col as any).selectedByName }}
                </div>
              </div>
              <div v-else-if="col.name === 'profile_name'" class="row items-center">
                <LeagueLevel :level="level" v-if="level" />
                <span v-else>{{ col.label }}</span>
              </div>
              <span v-else>{{ col.label }}</span>
            </q-th>
          </q-tr>
        </template>

        <template #body-cell-profile_name="props">
          <q-td :props="props" class="text-left profile-cell">
            <div class="row items-center no-wrap">
              <template v-if="props.row.username">
                <div class="row items-center no-wrap q-gutter-x-sm">
                  <div v-if="isMobile">
                    <span
                      class="text-weight-bold cursor-pointer username-link"
                      @click="$router.push({ name: 'user-detail', params: { username: props.row.username } })"
                    >
                      {{ props.row.username }}
                    </span>
                    <KennerTooltip>{{ props.row.username }}</KennerTooltip>
                  </div>
                  <div v-else class="column">
                    <span
                      class="text-subtitle2 text-weight-bold line-height-1 cursor-pointer username-link"
                      @click="$router.push({ name: 'user-detail', params: { username: props.row.username } })"
                    >
                      {{ props.row.username }}
                    </span>
                    <span
                      v-if="props.row.profile_name && props.row.profile_name !== props.row.username"
                      class="text-caption text-grey-6"
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
                    color="grey-2"
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
              <div v-if="!isMobile && props.rowIndex === 0 && (standings?.selected_games && standings.selected_games.length > 0)" class="leader-crown q-ml-sm">
                <q-icon
                  name="emoji_events"
                  color="amber-8"
                  size="18px"
                />
                <KennerTooltip>League Leader</KennerTooltip>
              </div>

              <!-- Tie Group Indicator -->
              <template v-if="props.row.unresolved_tie_group">
                <span class="text-orange q-ml-xs cursor-pointer" style="font-size: 1.1rem; line-height: 1;">
                  *
                  <KennerTooltip>unresolved tie</KennerTooltip>
                </span>
              </template>
              <template v-else-if="props.row.resolved_tie_reason">
                <span class="text-green q-ml-xs cursor-pointer" style="font-size: 1.1rem; line-height: 1;">
                  *
                  <KennerTooltip>{{ props.row.resolved_tie_reason }}</KennerTooltip>
                </span>
              </template>
            </div>
          </q-td>
        </template>

        <!-- Total column -->
        <template #body-cell-total="props">
          <q-td :props="props" class="text-right" style="padding: 4px 8px">
            <div class="text-weight-bold text-caption">
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
            <!-- Tie Breaker Info Tooltip -->
            <KennerTooltip v-if="props.value?.decisive_tie_breaker_name">
              Resolved by {{ props.value.decisive_tie_breaker_name }}: {{ props.value.tie_breaker_value }}
            </KennerTooltip>


            <div
              v-if="
                props.value && (props.value.points || props.value.league_points)
              "
              class="column items-center"
              style="line-height: 1.1"
            >
              <div
                v-if="props.value.points"
                class="text-weight-bold row items-baseline"
                style="font-size: 0.9rem"
              >
                <span>{{ displayPointsValue(props.value.points, (props.col as any).hasPoints) }}</span>
                <span
                  v-if="(props.col as any).hasPoints"
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
      <LoadingSpinner v-else-if="loading" text="Loading standings..." />

      <!-- Empty state -->
      <div v-else-if="standings && standings.standings.length === 0 && standings.selected_games.length === 0" class="column items-center q-pa-xl text-grey-6 bg-standings-table rounded-borders">
        <q-icon name="upcoming" size="40px" class="q-mb-sm opacity-50" />
        <div class="text-subtitle2">No participants yet</div>
        <div class="text-caption">The standings will appear here once the season starts.</div>
      </div>

      <!-- Unresolved Tie Info (only when the league is fully played) -->
      <div
        v-if="leagueId && standings?.all_games_finished && standings?.tie_groups?.some(g => g.unresolved)"
        class="q-mt-md q-mb-md"
      >
        <div class="unresolved-card">
          <div class="unresolved-card__header">
            <q-icon name="emoji_events" size="18px" class="unresolved-card__icon" />
            <div class="unresolved-card__title">Unresolved tie</div>
            <q-badge class="unresolved-card__badge" rounded>
              {{ standings.tie_groups.filter(g => g.unresolved).length }}
            </q-badge>
          </div>
          <div class="unresolved-card__body">
            <div
              v-for="grp in standings.tie_groups.filter(g => g.unresolved)"
              :key="grp.group_key"
              class="unresolved-card__group"
            >
              <template v-for="(m, idx) in grp.members" :key="m.player_profile_id">
                <span class="unresolved-card__player">{{ m.profile_name }}</span>
                <span
                  v-if="idx < grp.members.length - 1"
                  class="unresolved-card__vs"
                >vs</span>
              </template>
            </div>
          </div>
          <div class="unresolved-card__hint">
            Awaiting tie-break decision.
          </div>
        </div>
      </div>

      <!-- Footer Actions -->
<!--      <div v-if="standings && standings.season_id" class="row justify-end q-mt-md">-->
<!--        <KennerButton-->
<!--          flat-->
<!--          color="primary"-->
<!--          icon="visibility"-->
<!--          label="View Season Overview"-->
<!--          size="sm"-->
<!--          :to="{ name: 'season-overview', params: { id: standings.season_id } }"-->
<!--        />-->
<!--      </div>-->

<!--      &lt;!&ndash; Error state &ndash;&gt;-->
<!--      <div-->
<!--        v-else-if="error"-->
<!--        class="column items-center q-pa-md bg-standings-table rounded-borders"-->
<!--      >-->
<!--        <q-icon name="error_outline" size="24px" color="negative" />-->
<!--        <span class="q-mt-xs text-negative text-caption">-->
<!--          Error loading standings-->
<!--        </span>-->
<!--        <KennerButton-->
<!--          outline-->
<!--          color="dark"-->
<!--          label="Retry"-->
<!--          size="sm"-->
<!--          class="q-mt-sm"-->
<!--          @click="fetchStandings"-->
<!--        />-->
<!--      </div>-->
    </div>
  </div>
</template>

<style scoped lang="scss">
.border-orange-2 {
  border: 1px solid #ffcc80;
}

.unresolved-card {
  position: relative;
  border-radius: 12px;
  padding: 14px 16px;
  background: linear-gradient(135deg, #fff7ed 0%, #fff1de 100%);
  border: 1px solid #fcd9a8;
  box-shadow: 0 2px 6px rgba(180, 100, 0, 0.08);
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background: linear-gradient(180deg, #f59e0b, #d97706);
  }

  &__header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
  }

  &__icon {
    color: #d97706;
  }

  &__title {
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.3px;
    text-transform: uppercase;
    color: #92400e;
  }

  &__badge {
    background: #d97706;
    color: #fff;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 2px 8px;
  }

  &__body {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 12px;
  }

  &__group {
    display: inline-flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
    padding: 6px 10px;
    background: rgba(255, 255, 255, 0.75);
    border: 1px solid rgba(217, 119, 6, 0.25);
    border-radius: 999px;
  }

  &__player {
    font-size: 0.8rem;
    font-weight: 600;
    color: #7c2d12;
  }

  &__vs {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #b45309;
    opacity: 0.75;
  }

  &__hint {
    margin-top: 8px;
    font-size: 0.7rem;
    color: #92400e;
    opacity: 0.8;
    font-style: italic;
  }
}

:global(.body--dark) .unresolved-card {
  background: linear-gradient(135deg, rgba(120, 53, 15, 0.45) 0%, rgba(180, 83, 9, 0.35) 100%);
  border-color: rgba(252, 211, 77, 0.35);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.35);

  .unresolved-card__title,
  .unresolved-card__hint {
    color: #fde68a;
  }
  .unresolved-card__icon {
    color: #fbbf24;
  }
  .unresolved-card__group {
    background: rgba(0, 0, 0, 0.25);
    border-color: rgba(251, 191, 36, 0.35);
  }
  .unresolved-card__player {
    color: #fde68a;
  }
  .unresolved-card__vs {
    color: #fbbf24;
  }
}

.username-link {
  transition: color 0.2s ease;
}
.username-link:hover {
  color: var(--q-primary);
  text-decoration: underline;
}
</style>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { api } from 'boot/axios';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import type { QTableColumn } from 'quasar';
import { useResponsive } from 'src/composables/responsive';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import LeagueLevel from 'components/season/LeagueLevel.vue';

const props = defineProps<{
  leagueId: number;
  prefetchedData?: StandingsData | null;
  level?: number | string;
}>();

const { isMobile } = useResponsive();

interface GameStats {
  points: string;
  league_points: string;
  rank: number;
  decisive_tie_breaker_name?: string;
  tie_breaker_value?: string;
}

interface Standing {
  player_profile_id: number;
  profile_name: string;
  username?: string;
  total_league_points: string;
  total_wins: string;
  games: Record<string, GameStats>;
  unresolved_tie_group?: string;
  resolved_tie_reason?: string;
}

interface TieGroupMember {
  player_profile_id: number;
  profile_name: string;
  user_id?: number;
  username?: string;
}

interface TieResolution {
  reason: string;
  reason_display: string;
  note?: string;
  is_resolved: boolean;
}

interface TieGroup {
  group_key: string;
  unresolved: boolean;
  members: TieGroupMember[];
  league_points?: string;
  wins?: string;
  resolution?: TieResolution;
}

interface SelectedGame {
  id: number;
  game_name: string;
  game_short_name: string;
  platform_name?: string;
  has_points: boolean; // 🔹 added
  selected_by_name?: string;
}

interface StandingsData {
  selected_games: SelectedGame[];
  standings: Standing[];
  season_id?: number;
  tie_groups?: TieGroup[];
  all_games_finished?: boolean;
}

const standings = ref<StandingsData | null>(props.prefetchedData || null);
const loading = ref(!props.prefetchedData);
const error = ref(false);

const fetchStandings = async () => {
  if (props.prefetchedData) return;
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

watch(() => props.prefetchedData, (newVal) => {
  if (newVal) {
    standings.value = newVal;
    loading.value = false;
  }
}, { immediate: true });

// initial load
if (!props.prefetchedData) {
  fetchStandings();
}

const tableColumns = computed<QTableColumn[]>(() => {
  if (!standings.value) return [];

  const cols: QTableColumn[] = [
    {
      name: 'profile_name',
      label: '',
      field: 'profile_name',
      align: 'left',
      sortable: false,
    },
  ];

  standings.value.selected_games?.forEach((game) => {
    cols.push({
      name: `game_${game.id}`,
      // 🔹 short name on mobile, full name otherwise
      label:
        isMobile.value && game.game_short_name
          ? game.game_short_name
          : game.game_name,
      field: `game_${game.id}`,
      align: 'center',
      selectedByName: game.selected_by_name,
      platformName: game.platform_name,
      hasPoints: game.has_points,
    });
  });

  cols.push({
    name: 'total',
    label: 'LP',
    field: 'total',
    align: 'right',
    sortable: false,
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
      unresolved_tie_group: standing.unresolved_tie_group,
      resolved_tie_reason: (() => {
        const group = standings.value?.tie_groups?.find(g => g.group_key === standing.unresolved_tie_group);
        return (group && !group.unresolved) ? group.resolution?.reason_display : undefined;
      })()
    };

    standings.value.selected_games?.forEach((game) => {
      const gameData = standing.games[game.id.toString()];
      row[`game_${game.id}`] = gameData || null;
    });

    return row;
  });
});

const rowClass = (row: any, index: number) => {
  // Only highlight if there are actually points (total > 0) or if games have been played
  // Actually, usually we only highlight if total_league_points is non-zero or if we want to show current leader even at 0-0.
  // The user said "just headers with profile names", so maybe don't highlight yet?
  // But if we use index === 0, it will highlight the first person.
  // Let's check if there are any games.
  const hasGames = standings.value?.selected_games && standings.value.selected_games.length > 0;
  if (!hasGames) return '';
  return index === 0 ? 'league-leader-row' : '';
};

const formatNumber = (value: string | number): string => {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if ((num as number) === 0) return '0';
  if (!num) return '-';
  return (num as number) % 1 === 0 ? (num as number).toFixed(0) : String(num);
};

function displayPointsValue(points: string, hasPoints: boolean) {
  if (!hasPoints) {
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
        // Fallback for positions > 4 if they occur
        if (parseFloat(points) < 0) {
          return `${Math.abs(Math.round(parseFloat(points)))}th`;
        }
    }
  }
  return formatNumber(points);
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

</script>

<style scoped lang="scss">

.header-row {
  background-color: var(--standings-header-bg, #f8f9fa);
  border-bottom: 2px solid rgba(0, 0, 0, 0.05);
}

.profile-cell {
  padding: 8px 12px;
}

.leader-crown {
  animation: float 2s ease-in-out infinite;
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-2px); }
  100% { transform: translateY(0px); }
}

.league-leader-row {
  background-color: var(--standings-leader-bg, #fffaf0) !important; /* very light orange */
}

.bg-standings-table {
  background: white !important;
  color: #2c3e50;
}

:global(.body--dark .bg-standings-table) {
  background: #1d1d1d !important;
  color: #ececec;
  --standings-header-bg: #262626;
  --standings-leader-bg: #2d281e;
}

:global(.body--dark .bg-standings-table .header-row),
:global(.body--dark .bg-standings-table thead tr) {
  background-color: #262626 !important;
  border-bottom-color: rgba(255, 255, 255, 0.08) !important;
}

:global(.body--dark .bg-standings-table thead tr th) {
  color: #cccccc !important;
}

:global(.body--dark .bg-standings-table tbody tr td) {
  color: #ececec !important;
  border-color: rgba(255, 255, 255, 0.05) !important;
}

:global(.body--dark .bg-standings-table .league-leader-row td) {
  background-color: #2d281e !important;
}

.line-height-1 {
  line-height: 1.1;
}

/* Ensure the background doesn't override the hover effect of q-table if any */
:global(.q-table tbody tr:hover td.bg-amber-1),
:global(.q-table tbody tr:hover td.bg-blue-grey-1),
:global(.q-table tbody tr:hover td.bg-brown-1),
:global(.q-table tbody tr.bg-orange-1:hover) {
  filter: brightness(0.97);
}

:global(.body--dark .q-table tbody tr:hover td.bg-amber-1),
:global(.body--dark .q-table tbody tr:hover td.bg-blue-grey-1),
:global(.body--dark .q-table tbody tr:hover td.bg-brown-1) {
  filter: brightness(1.2);
}

:global(.body--dark .bg-standings-table .bg-amber-1) {
  background: rgba(255, 193, 7, 0.18) !important;
  color: #ffe082 !important;
}
:global(.body--dark .bg-standings-table .bg-blue-grey-1) {
  background: rgba(144, 164, 174, 0.18) !important;
  color: #cfd8dc !important;
}
:global(.body--dark .bg-standings-table .bg-brown-1) {
  background: rgba(141, 110, 99, 0.22) !important;
  color: #d7ccc8 !important;
}

.overflow-auto {
  scrollbar-width: thin;
  scrollbar-color: #e0e0e0 transparent;
}
</style>

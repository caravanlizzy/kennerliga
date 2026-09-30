<template>
  <!-- Loading -->
  <LoadingSpinner v-if="loading" />
  <ErrorDisplay v-if="error" :error="error ? 'Failed to load leaderboard' : ''" />

  <!-- Content -->
  <div
    v-else-if="standings && standings.standings.length > 0"
    class="leaderboard-container"
  >
    <!-- Table -->
    <div class="table-responsive-wrapper">
      <q-markup-table flat dense separator="none" class="leaderboard-table bg-transparent">
        <thead>
        <tr class="header-row">
          <th class="rank-col text-center">Rank</th>
          <th class="text-left player-col">Player</th>

          <template v-if="!showAllLeagues">
            <th class="text-center stat-col">
              <div class="column items-center">
                <span class="pos-badge pos-badge--1st">1st</span>
              </div>
            </th>

            <th class="text-center stat-col">
              <div class="column items-center">
                <span class="pos-badge pos-badge--2nd">2nd</span>
              </div>
            </th>

            <th class="text-center stat-col">
              <div class="column items-center">
                <span class="pos-badge pos-badge--3rd">3rd</span>
              </div>
            </th>

            <th class="text-center stat-col">
              <div class="column items-center">
                <span class="pos-badge pos-badge--4th">4th</span>
              </div>
            </th>
          </template>

          <template v-else>
            <template v-for="level in standings.levels" :key="level">
              <th class="text-center level-group-header">
                <div class="column items-center">
                  <LeagueLevel badge :level="level" class="q-mb-xs" />
                  <div class="row justify-center items-center no-wrap pos-mini-header">
                    <span class="pos-mini-label pos-mini-label--1">1st</span>
                    <div class="pos-sep"></div>
                    <span class="pos-mini-label pos-mini-label--2">2nd</span>
                    <div class="pos-sep"></div>
                    <span class="pos-mini-label pos-mini-label--3">3rd</span>
                    <div class="pos-sep"></div>
                    <span class="pos-mini-label pos-mini-label--4">4th</span>
                  </div>
                </div>
              </th>
            </template>
          </template>
        </tr>
        </thead>

        <tbody class="divide-y">
        <template
          v-for="(row, index) in standings.standings"
          :key="row.player_profile_id"
        >
          <!-- League level header (e.g. League 1) -->
          <tr v-if="index === 0 || bestLeague(row) !== bestLeague(standings.standings[index-1])" class="league-header-row">
            <td :colspan="showAllLeagues ? 2 + standings.levels.length : 6" class="q-pa-none">
              <div class="row items-center q-gutter-x-sm q-mt-md q-mb-xs q-px-sm">
                <div
                  v-if="bestLeague(row)"
                  class="league-header-badge"
                  :style="{
                    backgroundColor: getHexLeagueColor(bestLeague(row)!),
                  }"
                >
                  L{{ bestLeague(row) }}
                </div>
                <span v-if="bestLeague(row)" class="text-weight-bolder text-grey-8 text-uppercase tracking-wider" style="font-size: 0.75rem">
                  League {{ bestLeague(row) }}
                </span>
                <q-separator class="col q-ml-sm opacity-40" horizontal />
              </div>
            </td>
          </tr>

          <tr
            class="leaderboard-row"
            :class="{
              'leaderboard-row--leader': index === 0,
              'leaderboard-row--podium': index < 3
            }"
          >
            <!-- Rank -->
            <td class="text-center rank-col">
              <div class="flex flex-center">
                <span
                  class="rank-badge"
                  :class="`rank-badge--${index}`"
                >
                  <q-icon v-if="index === 0" name="emoji_events" size="13px" class="q-mr-xs" />
                  {{ index + 1 }}
                </span>
              </div>
            </td>

            <!-- Player -->
            <td class="text-left player-col q-py-sm">
              <div class="row items-center q-gutter-x-sm no-wrap">
                <UserAvatar
                  :display-username="row.profile_name || row.username"
                  :navigation-name="row.username"
                  :shape="getAvatarShape(row)"
                  :color="getAvatarColor(row)"
                  size="30px"
                  border
                />
                <div class="column ellipsis">
                  <span
                    class="text-body2 text-weight-bolder leaderboard-player-name cursor-pointer username-link ellipsis"
                    @click="$router.push({ name: 'user-detail', params: { username: row.username } })"
                  >{{ row.profile_name }}</span>
                  <span
                    v-if="row.profile_name && row.username && row.profile_name !== row.username"
                    class="text-caption text-grey-6 ellipsis"
                    style="font-size: 0.7rem; line-height: 1.1;"
                  >
                    @{{ row.username }}
                  </span>
                </div>
              </div>
            </td>

            <template v-if="!showAllLeagues">
              <!-- 1st -->
              <td class="text-center stat-col">
                <span
                  v-if="getHighestLeagueCounts(row).first > 0"
                  class="count-badge count-badge--first"
                >
                  {{ getHighestLeagueCounts(row).first }}
                </span>
                <span v-else class="text-grey-4 text-weight-medium">·</span>
              </td>

              <!-- 2nd -->
              <td class="text-center stat-col">
                <span
                  v-if="getHighestLeagueCounts(row).second > 0"
                  class="count-badge count-badge--second"
                >
                  {{ getHighestLeagueCounts(row).second }}
                </span>
                <span v-else class="text-grey-4 text-weight-medium">·</span>
              </td>

              <!-- 3rd -->
              <td class="text-center stat-col">
                <span
                  v-if="getHighestLeagueCounts(row).third > 0"
                  class="count-badge count-badge--third"
                >
                  {{ getHighestLeagueCounts(row).third }}
                </span>
                <span v-else class="text-grey-4 text-weight-medium">·</span>
              </td>

              <!-- 4th -->
              <td class="text-center stat-col">
                <span
                  v-if="getHighestLeagueCounts(row).fourth > 0"
                  class="count-badge count-badge--fourth"
                >
                  {{ getHighestLeagueCounts(row).fourth }}
                </span>
                <span v-else class="text-grey-4 text-weight-medium">·</span>
              </td>
            </template>

            <template v-else>
              <template v-for="level in standings.levels" :key="level">
                <td class="text-center q-px-xs stat-col-multi">
                  <div class="row justify-center items-center no-wrap level-counts-row">
                    <div class="column items-center pos-num">
                      <span :class="row.per_level[level]?.first ? 'text-weight-bolder text-amber-9' : 'text-grey-4'">
                        {{ row.per_level[level]?.first || '·' }}
                      </span>
                    </div>
                    <div class="pos-sep"></div>
                    <div class="column items-center pos-num">
                      <span :class="row.per_level[level]?.second ? 'text-weight-bold text-blue-grey-7' : 'text-grey-4'">
                        {{ row.per_level[level]?.second || '·' }}
                      </span>
                    </div>
                    <div class="pos-sep"></div>
                    <div class="column items-center pos-num">
                      <span :class="row.per_level[level]?.third ? 'text-weight-bold text-brown-6' : 'text-grey-4'">
                        {{ row.per_level[level]?.third || '·' }}
                      </span>
                    </div>
                    <div class="pos-sep"></div>
                    <div class="column items-center pos-num">
                      <span :class="row.per_level[level]?.fourth ? 'text-weight-medium text-grey-7' : 'text-grey-4'">
                        {{ row.per_level[level]?.fourth || '·' }}
                      </span>
                    </div>
                  </div>
                </td>
              </template>
            </template>
          </tr>
        </template>
        </tbody>
      </q-markup-table>
    </div>

    <!-- Note footer -->
    <div class="leaderboard-footer q-px-md q-py-sm text-caption text-grey-6 row items-center justify-between wrap q-gutter-y-xs">
      <div class="row items-center q-gutter-x-xs">
        <q-icon name="info" size="14px" color="grey-6" />
        <span>Ranked by highest league achieved (L1 top) and season placements.</span>
      </div>
      <div class="text-caption text-grey-5">
        {{ standings.standings.length }} {{ standings.standings.length === 1 ? 'player' : 'players' }}
      </div>
    </div>
  </div>

  <!-- No data -->
  <div v-else class="column items-center q-pa-xl text-grey-6 leaderboard-empty">
    <q-icon name="stars" size="48px" class="q-mb-sm opacity-20" />
    <div class="text-subtitle1 text-weight-bold">No Leaderboard Data</div>
    <div class="text-caption">Leaderboard statistics will appear here after the seasons conclude.</div>
  </div>
</template>

<script setup lang="ts">
import { fetchYearLeaderboard } from 'src/services/statisticsService';
import type {
  TPerLevelCounts,
  TPlayerYearStanding,
  TYearLeaderboard,
} from 'src/types';
import { ref, watch } from 'vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import ErrorDisplay from 'components/base/ErrorDisplay.vue';
import { leagueColors } from 'src/composables/leagueColors';
import { useCachedResource } from 'src/composables/cachedResource';
import LeagueLevel from 'components/season/LeagueLevel.vue';
import UserAvatar from 'components/ui/UserAvatar.vue';
import { useUserStore } from 'stores/userStore';

const props = defineProps<{ year: number }>();
const { getHexLeagueColor } = leagueColors();
const userStore = useUserStore();

function getAvatarShape(row: TPlayerYearStanding) {
  if (row.username && userStore.user?.username === row.username && userStore.user?.avatar_shape) {
    return userStore.user.avatar_shape;
  }
  return row.avatar_shape;
}

function getAvatarColor(row: TPlayerYearStanding) {
  if (row.username && userStore.user?.username === row.username && userStore.user?.avatar_color !== undefined) {
    return userStore.user.avatar_color;
  }
  return row.avatar_color;
}

const error = ref(false);
const showAllLeagues = defineModel<boolean>('showAllLeagues', { default: false });

// Stale-while-revalidate cache with a module-level `cacheKey`, so the
// leaderboard survives component unmount/remount (Hall of Fame section on
// the home page). The key is per-year, so switching years is instant on
// the second visit.
const {
  data: standings,
  loading,
  load: loadStandings,
} = useCachedResource<number, TYearLeaderboard>(
  async (year) => {
    error.value = false;
    try {
      return await fetchYearLeaderboard(year);
    } catch (e) {
      error.value = true;
      throw e;
    }
  },
  { cacheKey: 'leaderboard' }
);

function fetchStandings(): void {
  void loadStandings(props.year);
}

function bestLeague(row: TPlayerYearStanding): number | null {
  const levels = Object.entries(row.per_level)
    .filter(([, c]) => c.first || c.second || c.third || c.fourth)
    .map(([level]) => Number(level));

  if (levels.length === 0) return null;
  return Math.min(...levels);
}

function getHighestLeagueCounts(row: TPlayerYearStanding): TPerLevelCounts {
  const highestLvl = bestLeague(row);
  if (highestLvl === null) return { first: 0, second: 0, third: 0, fourth: 0 };
  return row.per_level[String(highestLvl)] || { first: 0, second: 0, third: 0, fourth: 0 };
}

watch(
  () => props.year,
  () => fetchStandings(),
  { immediate: true }
);
</script>

<style scoped lang="scss">
.leaderboard-container {
  border-radius: 12px;
  overflow: hidden;
  background: #ffffff;
}

.table-responsive-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.leaderboard-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;

  thead tr.header-row {
    background: #f8fafc;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);

    th {
      font-size: 0.72rem;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      font-weight: 700;
      color: #64748b;
      padding: 10px 8px;
    }
  }
}

.rank-col {
  width: 60px;
  min-width: 50px;
  padding: 8px 4px 8px 12px !important;
}

.player-col {
  min-width: 160px;
}

.stat-col {
  width: 70px;
  min-width: 60px;
}

.stat-col-multi {
  min-width: 110px;
}

.pos-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 6px;
  letter-spacing: 0.03em;

  &--1st {
    background: rgba(245, 158, 11, 0.12);
    color: #b45309;
  }
  &--2nd {
    background: rgba(148, 163, 184, 0.15);
    color: #475569;
  }
  &--3rd {
    background: rgba(217, 119, 6, 0.12);
    color: #9a3412;
  }
  &--4th {
    background: rgba(100, 116, 139, 0.1);
    color: #64748b;
  }
}

.pos-mini-header {
  gap: 2px;
}

.pos-mini-label {
  font-size: 0.65rem;
  font-weight: 700;

  &--1 { color: #b45309; }
  &--2 { color: #64748b; }
  &--3 { color: #9a3412; }
  &--4 { color: #94a3b8; }
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 26px;
  height: 24px;
  padding: 0 6px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 800;
  background: #f1f5f9;
  color: #64748b;
  transition: all 0.2s ease;

  // Shared gold/silver/bronze styling
  &--0 {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    color: #92400e;
    border: 1px solid rgba(245, 158, 11, 0.3);
    font-weight: 900;
  }
  &--1 {
    background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
    color: #334155;
    border: 1px solid rgba(148, 163, 184, 0.3);
  }
  &--2 {
    background: linear-gradient(135deg, #ffedd5 0%, #fed7aa 100%);
    color: #9a3412;
    border: 1px solid rgba(249, 115, 22, 0.3);
  }
}

.leaderboard-row {
  transition: background-color 0.15s ease;

  &:hover {
    background-color: rgba(248, 250, 252, 0.8);
  }

  &--leader {
    background-color: rgba(254, 243, 199, 0.15);
  }
}

.count-badge {
  display: inline-block;
  font-weight: 800;
  font-size: 0.88rem;

  &--first {
    color: #b45309;
    font-size: 0.95rem;
  }
  &--second {
    color: #334155;
  }
  &--third {
    color: #9a3412;
  }
  &--fourth {
    color: #64748b;
  }
}

.level-counts-row {
  font-size: 0.75rem;
}

.league-header-badge {
  padding: 2px 7px;
  border-radius: 4px;
  color: white;
  font-size: 10px;
  font-weight: 800;
  line-height: 1.2;
}

.tracking-wider {
  letter-spacing: 0.05em;
}

.pos-sep {
  width: 1px;
  height: 10px;
  background-color: rgba(0, 0, 0, 0.08);
  margin: 0 4px;
}

.pos-num {
  min-width: 16px;
}

.divide-y > tr:not(:first-child) {
  border-top: 1px solid rgba(0, 0, 0, 0.04);
}

.username-link {
  color: #1e293b;
  transition: color 0.15s ease;

  &:hover {
    color: var(--q-primary);
  }
}

.leaderboard-footer {
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  background: #fafafa;
}

.opacity-20 {
  opacity: 0.2;
}

.opacity-40 {
  opacity: 0.4;
}
</style>

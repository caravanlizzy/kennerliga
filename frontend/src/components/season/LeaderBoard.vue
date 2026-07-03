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
    <q-markup-table flat dense separator="none" class="leaderboard-table bg-transparent">
      <thead>
      <tr class="text-uppercase text-grey-6 text-caption text-weight-bold header-row">
        <th class="text-left q-pl-lg" style="width: 56px">#</th>
        <th class="text-left player-column">Player</th>

        <template v-if="!showAllLeagues">
          <th class="text-center">
              <div class="column items-center">
                <q-icon name="emoji_events" class="text-amber-8" size="22px" />
                <span class="q-mt-xs">1st</span>
              </div>
          </th>

          <th class="text-center">
              <div class="column items-center">
                <q-icon name="military_tech" class="text-blue-grey-4" size="22px" />
                <span class="q-mt-xs">2nd</span>
              </div>
          </th>

          <th class="text-center">
              <div class="column items-center">
                <q-icon name="military_tech" class="text-brown-5" size="22px" />
                <span class="q-mt-xs">3rd</span>
              </div>
          </th>

          <th class="text-center">
              <div class="column items-center">
                <q-icon name="flag" class="text-red-5" size="22px" />
                <span class="q-mt-xs">4th</span>
              </div>
          </th>
        </template>

        <template v-else>
          <template v-for="level in standings.levels" :key="level">
            <th class="text-center level-group-header" :style="{ borderLeft: '1.5px solid rgba(54, 64, 88, 0.12)' }">
              <div class="column items-center">
                <span class="text-caption text-weight-bolder text-primary q-mb-xs">L{{ level }}</span>
                <div class="row justify-center items-center no-wrap">
                  <q-icon name="emoji_events" class="text-amber-8" size="14px" />
                  <div class="pos-sep"></div>
                  <q-icon name="military_tech" class="text-blue-grey-4" size="14px" />
                  <div class="pos-sep"></div>
                  <q-icon name="military_tech" class="text-brown-5" size="14px" />
                  <div class="pos-sep"></div>
                  <q-icon name="flag" class="text-red-5" size="14px" />
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
        <!-- League level separator (e.g. L1 to L2) -->
        <tr v-if="index > 0 && bestLeague(row) !== bestLeague(standings.standings[index-1])" class="league-separator-row">
          <td :colspan="showAllLeagues ? 2 + standings.levels.length : 6" class="q-pa-none">
            <div class="league-separator-divider"></div>
          </td>
        </tr>

        <tr
          class="leaderboard-row"
          :class="{
            'top-rank-bg': index === 0
          }"
        >

          <!-- Rank (with subtle league level dot) -->
          <td class="text-left q-pl-lg leaderboard-rank-text">
            <div class="row items-center no-wrap q-gutter-x-sm">
              <div
                class="rank-badge"
                :class="{
                  'rank-badge--gold': index === 0,
                  'rank-badge--silver': index === 1,
                  'rank-badge--bronze': index === 2,
                }"
              >
                {{ index + 1 }}
              </div>
              <div
                v-if="bestLeague(row)"
                class="league-dot"
                :style="{ backgroundColor: getHexLeagueColor(bestLeague(row)!) }"
              >
                <q-tooltip anchor="center right" self="center left">
                  League {{ bestLeague(row) }}
                </q-tooltip>
              </div>
            </div>
          </td>

          <!-- Player -->
          <td class="text-left relative-position q-py-md">
            <div class="row items-center q-gutter-x-md">
              <div class="column">
                <div class="row items-center q-gutter-x-sm">
                  <span
                    class="text-subtitle2 text-weight-bold leaderboard-player-name cursor-pointer username-link"
                    @click="$router.push({ name: 'user-detail', params: { username: row.username } })"
                  >{{ row.profile_name }}</span>
                  <q-icon
                    v-if="index === 0"
                    name="stars"
                    color="amber-9"
                    size="18px"
                  >
                    <q-tooltip>Leader</q-tooltip>
                  </q-icon>
                </div>
              </div>
            </div>
          </td>

          <template v-if="!showAllLeagues">
            <!-- 1st -->
            <td class="text-center border-left-subtle-2">
                <span
                  v-if="getHighestLeagueCounts(row).first > 0"
                  class="text-weight-bold leaderboard-count-text"
                >
                  {{ getHighestLeagueCounts(row).first }}
                </span>
                <span v-else class="text-grey-4">-</span>
            </td>

            <!-- 2nd -->
            <td class="text-center border-left-subtle-2">
                <span
                  v-if="getHighestLeagueCounts(row).second > 0"
                  class="text-weight-bold leaderboard-count-text-subtle"
                >
                  {{ getHighestLeagueCounts(row).second }}
                </span>
                <span v-else class="text-grey-4">-</span>
            </td>

            <!-- 3rd -->
            <td class="text-center border-left-subtle-2">
                <span
                  v-if="getHighestLeagueCounts(row).third > 0"
                  class="text-weight-bold leaderboard-count-text-subtle"
                >
                  {{ getHighestLeagueCounts(row).third }}
                </span>
                <span v-else class="text-grey-4">-</span>
            </td>

            <!-- 4th -->
            <td class="text-center border-left-subtle-2">
                <span
                  v-if="getHighestLeagueCounts(row).fourth > 0"
                  class="text-weight-bold leaderboard-count-text-subtle"
                >
                  {{ getHighestLeagueCounts(row).fourth }}
                </span>
                <span v-else class="text-grey-4">-</span>
            </td>
          </template>

          <template v-else>
            <template v-for="level in standings.levels" :key="level">
              <td class="text-center q-px-sm" :style="{ borderLeft: '1.5px solid rgba(54, 64, 88, 0.08)' }">
                <div class="row justify-center items-center no-wrap">
                  <div class="column items-center pos-num">
                    <span :class="row.per_level[level]?.first ? 'text-weight-bold leaderboard-count-text' : 'text-grey-4'" style="font-size: 11px">
                      {{ row.per_level[level]?.first || '-' }}
                    </span>
                  </div>
                  <div class="pos-sep"></div>
                  <div class="column items-center pos-num">
                    <span :class="row.per_level[level]?.second ? 'text-weight-bold leaderboard-count-text-subtle' : 'text-grey-4'" style="font-size: 11px">
                      {{ row.per_level[level]?.second || '-' }}
                    </span>
                  </div>
                  <div class="pos-sep"></div>
                  <div class="column items-center pos-num">
                    <span :class="row.per_level[level]?.third ? 'text-weight-bold leaderboard-count-text-subtle' : 'text-grey-4'" style="font-size: 11px">
                      {{ row.per_level[level]?.third || '-' }}
                    </span>
                  </div>
                  <div class="pos-sep"></div>
                  <div class="column items-center pos-num">
                    <span :class="row.per_level[level]?.fourth ? 'text-weight-bold leaderboard-count-text-subtle' : 'text-grey-4'" style="font-size: 11px">
                      {{ row.per_level[level]?.fourth || '-' }}
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

    <!-- Legend -->
    <div class="q-px-lg q-py-sm text-caption text-grey-7 border-top-subtle">
      <div class="row items-center q-gutter-x-xs">
        <q-icon name="info" size="14px" />
        <span>
          <strong>Legend:</strong> The colored dot next to the rank indicates the highest league level a player has participated in.
          Higher league participation results in a higher leaderboard position.
        </span>
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
import { api } from 'boot/axios';
import { ref, watch } from 'vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import ErrorDisplay from 'components/base/ErrorDisplay.vue';
import { leagueColors } from 'src/composables/leagueColors';
import { useCachedResource } from 'src/composables/cachedResource';

const props = defineProps<{ year: number }>();
const {  getHexLeagueColor } = leagueColors();

interface PerLevelCounts {
  first: number;
  second: number;
  third: number;
  fourth: number;
}
interface PlayerYearStanding {
  player_profile_id: number;
  profile_name: string;
  username: string;
  per_level: Record<string, PerLevelCounts>;
}
interface LeaderBoardResponse {
  year: number;
  levels: number[];
  standings: PlayerYearStanding[];
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
} = useCachedResource<number, LeaderBoardResponse>(
  async (year) => {
    error.value = false;
    try {
      const { data } = await api.get<LeaderBoardResponse>(
        `leaderboard/?year=${year}`
      );
      return data;
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

function bestLeague(row: PlayerYearStanding): number | null {
  const levels = Object.entries(row.per_level)
    .filter(([, c]) => c.first || c.second || c.third || c.fourth)
    .map(([level]) => Number(level));

  if (levels.length === 0) return null;
  return Math.min(...levels);
}

function getHighestLeagueCounts(row: PlayerYearStanding): PerLevelCounts {
  const highestLvl = bestLeague(row);
  if (highestLvl === null) return { first: 0, second: 0, third: 0, fourth: 0 };
  return row.per_level[String(highestLvl)] || { first: 0, second: 0, third: 0, fourth: 0 };
}

// lower league number => more "winner-like" color
watch(
  () => props.year,
  () => fetchStandings(),
  { immediate: true }
);
</script>

<style scoped lang="scss">
.leaderboard-container, .leaderboard-empty {
  overflow: auto;
  background: var(--leaderboard-bg, rgba(255, 255, 255, 0.65));
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--leaderboard-border, rgba(54, 64, 88, 0.08));
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(54, 64, 88, 0.04);
}

.leaderboard-header {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.5) 0%, rgba(255, 255, 255, 0.2) 100%);
  border-bottom: 1px solid var(--leaderboard-border, rgba(54, 64, 88, 0.08));
}

.leaderboard-header__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--q-primary) 0%, var(--q-accent) 100%);
  color: #fff;
}

:global(.body--dark) .leaderboard-header {
  background: linear-gradient(135deg, rgba(40, 40, 40, 0.6) 0%, rgba(30, 30, 30, 0.3) 100%);
}

:global(.body--dark) .rank-badge {
  background: rgba(255, 255, 255, 0.08);
  color: var(--leaderboard-rank-text, #bdbdbd);
}

:global(.body--dark) .league-toggle {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.08);
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 28px;
  padding: 0 8px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 13px;
  color: var(--leaderboard-rank-text, #757575);
  background: rgba(54, 64, 88, 0.06);
}

.rank-badge--gold {
  background: linear-gradient(135deg, #ffd54f 0%, #ffb300 100%);
  color: #5d4037;
  box-shadow: 0 2px 8px rgba(255, 179, 0, 0.35);
}

.rank-badge--silver {
  background: linear-gradient(135deg, #eceff1 0%, #b0bec5 100%);
  color: #37474f;
  box-shadow: 0 2px 8px rgba(176, 190, 197, 0.4);
}

.rank-badge--bronze {
  background: linear-gradient(135deg, #d7a17a 0%, #a1683a 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(161, 104, 58, 0.35);
}

:global(.body--dark) {
  .leaderboard-container, .leaderboard-empty {
    --leaderboard-bg: rgba(30, 30, 30, 0.8);
    --leaderboard-border: rgba(255, 255, 255, 0.1);
    --leaderboard-header-bg: rgba(40, 40, 40, 0.5);
    --leaderboard-header-text: #bdbdbd;
    --leaderboard-row-bg: #1d1d1d;
    --leaderboard-row-hover: #262626;
    --leaderboard-row-border: rgba(255, 255, 255, 0.05);
    --leaderboard-player-text: #ececec;
    --leaderboard-rank-text: #9e9e9e;
    --leaderboard-count-text: #ececec;
    --leaderboard-count-text-subtle: #bdbdbd;
    --leaderboard-sep: rgba(255, 255, 255, 0.1);
    --toggle-bg: #1d1d1d;
  }
}

.leaderboard-header-text { color: var(--leaderboard-header-text, #616161); } /* text-grey-8 */
.leaderboard-player-name { color: var(--leaderboard-player-text, #212121); } /* text-grey-9 */
.username-link { transition: color 0.2s ease; }
.username-link:hover { color: var(--q-primary); text-decoration: underline; }
.leaderboard-rank-text { color: var(--leaderboard-rank-text, #757575); } /* text-grey-7 */
.leaderboard-count-text { color: var(--leaderboard-count-text, #212121); } /* text-grey-9 */
.leaderboard-count-text-subtle { color: var(--leaderboard-count-text-subtle, #424242); } /* text-grey-8 */

.leaderboard-table {
  min-width: 600px;

  @media (max-width: 600px) {
    min-width: 100%;
    table-layout: fixed;
  }
}

.player-column {
  width: 35%;
  @media (max-width: 600px) {
    width: auto;
    min-width: 120px;
  }
}

.league-toggle {
  flex: 0 0 auto;
  width: 200px;
  background: rgba(54, 64, 88, 0.06);
  border-radius: 999px;
  padding: 3px;
  border: 1px solid rgba(54, 64, 88, 0.06);

  :deep(.q-btn) {
    flex: 1 1 0;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    min-height: 28px;
    padding: 2px 10px;
    transition: all 0.2s ease;
  }

  :deep(.q-btn--active) {
    box-shadow: 0 2px 8px rgba(54, 64, 88, 0.15);
  }

  :deep(.q-btn__content) {
    white-space: nowrap;
  }

  @media (max-width: 480px) {
    width: 100%;
    margin-top: 12px;
  }
}

.header-row {
  background: var(--leaderboard-header-bg, rgba(248, 249, 250, 0.4));
  border-bottom: 1.5px solid var(--leaderboard-border, rgba(54, 64, 88, 0.1));
  height: 48px;
  letter-spacing: 0.5px;
}

.leaderboard-row {
  position: relative;
  transition: background-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
  border-bottom: 1px solid var(--leaderboard-row-border, rgba(0, 0, 0, 0.04));
  background: var(--leaderboard-row-bg, transparent);

  &:hover {
    background-color: var(--leaderboard-row-hover, rgba(255, 255, 255, 0.85)) !important;
    z-index: 1;
    box-shadow: 0 4px 16px rgba(54, 64, 88, 0.06);
  }
}

.league-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex: 0 0 auto;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.6), 0 1px 2px rgba(0, 0, 0, 0.08);
  cursor: help;
}

:global(.body--dark) .league-dot {
  box-shadow: 0 0 0 2px rgba(30, 30, 30, 0.6), 0 1px 2px rgba(0, 0, 0, 0.3);
}


.top-rank-bg {
  /* Subtle gold tint with left accent for the leader */
  background-image: linear-gradient(90deg, rgba(255, 193, 7, 0.08) 0%, rgba(255, 193, 7, 0) 60%) !important;
}

.league-indicator {
  font-size: 10px;
  padding: 2px 4px;
  font-weight: 700;
  line-height: 1;
}

.border-top-subtle {
  border-top: 1px solid rgba(54, 64, 88, 0.1);
}

.border-bottom-subtle {
  border-bottom: 1px solid rgba(54, 64, 88, 0.1);
}

.border-primary-1 {
  border: 1px solid var(--q-primary);
}

.pos-sep {
  width: 1px;
  height: 12px;
  background-color: var(--leaderboard-sep, rgba(0, 0, 0, 0.05));
  margin: 0 6px;
}

.pos-num {
  min-width: 16px;
}

.border-left-subtle-2 {
  border-left: 1px solid var(--leaderboard-sep, rgba(0, 0, 0, 0.08)) !important;
}

.divide-y tr:last-child {
  border-bottom: none;
}

.league-separator-row {
  background: var(--leaderboard-bg, rgba(255, 255, 255, 0.4));
}

.league-separator-divider {
  height: 2px;
  background-image: linear-gradient(to right, transparent 0%, rgba(54, 64, 88, 0.08) 50%, transparent 100%);
  margin: 1px 0;
}
</style>

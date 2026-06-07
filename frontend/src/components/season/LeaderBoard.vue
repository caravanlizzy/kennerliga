<template>
  <!-- Loading -->
  <LoadingSpinner v-if="loading" />
  <ErrorDisplay v-if="error" :error="error ? 'Failed to load leaderboard' : ''" />

  <!-- Content -->
  <div
    v-else-if="standings && standings.standings.length > 0"
    class="leaderboard-container"
  >
    <!-- View Toggle -->
    <div class="q-px-lg q-py-md row items-center justify-between border-bottom-subtle">
      <div class="row items-center q-gutter-x-sm">
        <q-icon name="analytics" color="primary" size="20px" />
        <span class="text-subtitle2 text-weight-bold leaderboard-header-text">Annual Leaderboard</span>
      </div>
      <q-btn-toggle
        v-model="showAllLeagues"
        toggle-color="primary"
        text-color="grey-7"
        unelevated
        dense
        no-caps
        spread
        class="league-toggle"
        :options="[
          { label: 'Highest', value: false },
          { label: 'All', value: true }
        ]"
      />
    </div>

    <!-- Table -->
    <q-markup-table flat dense separator="none" class="leaderboard-table bg-transparent">
      <thead>
      <tr class="text-uppercase text-grey-6 text-caption text-weight-bold header-row">
        <th class="q-pa-none" style="width: 4px"></th>
        <th class="text-left q-pl-lg" style="width: 40px">#</th>
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
          <td :colspan="showAllLeagues ? 3 + standings.levels.length : 7" class="q-pa-none">
            <div class="league-separator-divider"></div>
          </td>
        </tr>

        <tr
          class="leaderboard-row"
          :class="{
            'top-rank-bg': index === 0
          }"
        >

          <!-- League Level Indicator Strip -->
          <td class="q-pa-none relative-position" style="width: 4px; padding: 0 !important;">
            <div
              v-if="bestLeague(row)"
              class="league-strip"
              :style="{ backgroundColor: getHexLeagueColor(bestLeague(row)!) }"
            >
              <q-tooltip anchor="center right" self="center left">
                League {{ bestLeague(row) }}
              </q-tooltip>
            </div>
          </td>
          <!-- Rank -->
          <td class="text-left q-pl-lg text-weight-bold leaderboard-rank-text">
            {{ index + 1 }}
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
          <strong>Legend:</strong> The colored strip on the left indicates the highest league level a player has participated in.
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
import { leagueColors } from '../../composables/leagueColors';

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

const standings = ref<LeaderBoardResponse | null>(null);
const loading = ref(false);
const error = ref(false);
const showAllLeagues = ref(false);

async function fetchStandings(): Promise<void> {
  loading.value = true;
  error.value = false;
  standings.value = null;

  try {
    const { data } = await api.get<LeaderBoardResponse>(
      `leaderboard/?year=${props.year}`
    );
    standings.value = data;
  } catch (e) {
    console.error('Error loading yearly standings:', e);
    error.value = true;
  } finally {
    loading.value = false;
  }
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
  background: var(--leaderboard-bg, rgba(255, 255, 255, 0.4));
  backdrop-filter: blur(8px);
  border: 1px solid var(--leaderboard-border, rgba(54, 64, 88, 0.08));
  border-radius: 12px;
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
  background: rgba(0, 0, 0, 0.04);
  border-radius: 999px;
  padding: 2px;

  :deep(.q-btn) {
    flex: 1 1 0;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    min-height: 28px;
    padding: 2px 10px;
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
  background: var(--leaderboard-header-bg, rgba(248, 249, 250, 0.5));
  border-bottom: 1.5px solid var(--leaderboard-border, rgba(54, 64, 88, 0.12));
  height: 48px;
}

.leaderboard-row {
  position: relative;
  transition: all 0.2s ease;
  border-bottom: 1px solid var(--leaderboard-row-border, rgba(0, 0, 0, 0.04));
  background: var(--leaderboard-row-bg, white);

  &:hover {
    background-color: var(--leaderboard-row-hover, rgba(248, 250, 252, 1)) !important;
    z-index: 1;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
  }
}

.league-strip {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  z-index: 2;
}


.top-rank-bg {
  /* Using a very subtle amber overlay for the first rank, compatible with league backgrounds */
  background-image: linear-gradient(rgba(255, 215, 0, 0.05), rgba(255, 215, 0, 0.05)) !important;
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

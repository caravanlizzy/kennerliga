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
        <span class="text-subtitle2 text-weight-bold text-grey-8">League Statistics</span>
      </div>
      <q-btn-toggle
        v-model="showAllLeagues"
        toggle-color="primary"
        color="white"
        text-color="primary"
        unelevated
        dense
        rounded
        class="border-primary-1 full-width-mobile"
        :options="[
          { label: 'Highest League', value: false },
          { label: 'All Leagues', value: true }
        ]"
      />
    </div>

    <!-- Table -->
    <q-markup-table flat dense separator="none" class="leaderboard-table bg-transparent">
      <thead>
      <tr class="text-uppercase text-grey-6 text-caption text-weight-bold header-row">
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
            <th class="text-center level-group-header" :style="{ borderLeft: '1px solid rgba(0,0,0,0.05)' }">
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
        <tr
          class="leaderboard-row"
          :class="{
            'top-rank-bg': index === 0,
          }"
        >
          <!-- Rank -->
          <td class="text-left q-pl-lg text-weight-bold text-grey-7">
            {{ index + 1 }}
          </td>

          <!-- Player -->
          <td class="text-left relative-position q-py-md">
            <div class="row items-center q-gutter-x-md">
              <UserAvatar
                :display-username="row.profile_name"
                size="32px"
              />
              <div class="column">
                <div class="row items-center q-gutter-x-sm">
                  <span class="text-subtitle2 text-weight-bold text-grey-9">{{ row.profile_name }}</span>
                  <q-badge
                    v-if="bestLeague(row)"
                    outline
                    :color="leagueBadgeColor(bestLeague(row)!)"
                    class="league-indicator"
                  >
                    L{{ bestLeague(row) }}
                  </q-badge>
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
            <td class="text-center">
                <span
                  v-if="getHighestLeagueCounts(row).first > 0"
                  class="text-weight-bold text-grey-9"
                >
                  {{ getHighestLeagueCounts(row).first }}
                </span>
                <span v-else class="text-grey-4">-</span>
            </td>

            <!-- 2nd -->
            <td class="text-center border-left-subtle-2">
                <span
                  v-if="getHighestLeagueCounts(row).second > 0"
                  class="text-weight-bold text-grey-8"
                >
                  {{ getHighestLeagueCounts(row).second }}
                </span>
                <span v-else class="text-grey-4">-</span>
            </td>

            <!-- 3rd -->
            <td class="text-center border-left-subtle-2">
                <span
                  v-if="getHighestLeagueCounts(row).third > 0"
                  class="text-weight-bold text-grey-8"
                >
                  {{ getHighestLeagueCounts(row).third }}
                </span>
                <span v-else class="text-grey-4">-</span>
            </td>

            <!-- 4th -->
            <td class="text-center border-left-subtle-2">
                <span
                  v-if="getHighestLeagueCounts(row).fourth > 0"
                  class="text-weight-bold text-grey-8"
                >
                  {{ getHighestLeagueCounts(row).fourth }}
                </span>
                <span v-else class="text-grey-4">-</span>
            </td>
          </template>

          <template v-else>
            <template v-for="level in standings.levels" :key="level">
              <td class="text-center q-px-sm" :style="{ borderLeft: '1px solid rgba(0,0,0,0.03)' }">
                <div class="row justify-center items-center no-wrap">
                  <div class="column items-center pos-num">
                    <span :class="row.per_level[level]?.first ? 'text-weight-bold text-grey-9' : 'text-grey-4'" style="font-size: 11px">
                      {{ row.per_level[level]?.first || '-' }}
                    </span>
                  </div>
                  <div class="pos-sep"></div>
                  <div class="column items-center pos-num">
                    <span :class="row.per_level[level]?.second ? 'text-weight-bold text-grey-8' : 'text-grey-4'" style="font-size: 11px">
                      {{ row.per_level[level]?.second || '-' }}
                    </span>
                  </div>
                  <div class="pos-sep"></div>
                  <div class="column items-center pos-num">
                    <span :class="row.per_level[level]?.third ? 'text-weight-bold text-grey-8' : 'text-grey-4'" style="font-size: 11px">
                      {{ row.per_level[level]?.third || '-' }}
                    </span>
                  </div>
                  <div class="pos-sep"></div>
                  <div class="column items-center pos-num">
                    <span :class="row.per_level[level]?.fourth ? 'text-weight-bold text-grey-8' : 'text-grey-4'" style="font-size: 11px">
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
          <strong>Legend:</strong> "LX" indicates the highest league level a player has participated in at least once.
          Higher league participation (smaller X) results in a higher leaderboard position.
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
import UserAvatar from 'components/ui/UserAvatar.vue';

const props = defineProps<{ year: number }>();

interface PerLevelCounts {
  first: number;
  second: number;
  third: number;
  fourth: number;
}
interface PlayerYearStanding {
  player_profile_id: number;
  profile_name: string;
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

function totalPoints(row: PlayerYearStanding): number {
  const counts = getHighestLeagueCounts(row);
  return (counts.first * 4) + (counts.second * 3) + (counts.third * 2) + (counts.fourth * 1);
}

// lower league number => more "winner-like" color
function leagueBadgeColor(league: number): string {
  if (league <= 1) return 'amber-8'; // best
  if (league === 2) return 'blue-grey-5';
  if (league === 3) return 'brown-6';
  if (league === 4) return 'red-6';
  if (league <= 6) return 'deep-purple-6';
  if (league <= 10) return 'indigo-6';
  return 'grey-6';
}

watch(
  () => props.year,
  () => fetchStandings(),
  { immediate: true }
);
</script>

<style scoped lang="scss">
.leaderboard-container, .leaderboard-empty {
  overflow: auto;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(54, 64, 88, 0.08);
  border-radius: 12px;
}

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

.full-width-mobile {
  @media (max-width: 480px) {
    width: 100%;
    margin-top: 12px;

    :deep(.q-btn) {
      flex: 1;
    }
  }
}

.header-row {
  background: rgba(248, 249, 250, 0.5);
  border-bottom: 1px solid rgba(54, 64, 88, 0.05);
  height: 64px;
}

.leaderboard-row {
  position: relative;
  transition: all 0.2s ease;
  border-bottom: 1px solid rgba(0, 0, 0, 0.03);

  &:hover {
    background-color: rgba(255, 255, 255, 0.6) !important;
    z-index: 1;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
  }
}

.top-rank-bg {
  background-color: rgba(255, 249, 230, 0.4);
}

.league-indicator {
  font-size: 10px;
  padding: 2px 4px;
  font-weight: 700;
  line-height: 1;
}

.border-top-subtle {
  border-top: 1px solid rgba(54, 64, 88, 0.05);
}

.border-bottom-subtle {
  border-bottom: 1px solid rgba(54, 64, 88, 0.05);
}

.border-primary-1 {
  border: 1px solid var(--q-primary);
}

.pos-sep {
  width: 1px;
  height: 12px;
  background-color: rgba(0, 0, 0, 0.05);
  margin: 0 6px;
}

.pos-num {
  min-width: 16px;
}

.border-left-subtle-2 {
  border-left: 1px solid rgba(0, 0, 0, 0.03) !important;
}

.divide-y tr:last-child {
  border-bottom: none;
}
</style>

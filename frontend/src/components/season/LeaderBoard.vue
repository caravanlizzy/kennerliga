<template>
  <!-- Loading -->
  <LoadingSpinner v-if="loading" />
  <ErrorDisplay v-if="error" :error="error ? 'Failed to load leaderboard' : ''" />

  <!-- Content -->
  <div
    v-else-if="standings && standings.standings.length > 0"
    class="overflow-auto rounded-borders"
  >
    <!-- Table -->
    <q-markup-table flat dense separator="none" class="leaderboard-table bg-transparent">
      <thead>
      <tr class="text-uppercase text-grey-7 text-caption text-weight-bold header-row bg-grey-1">
        <th></th>
        <th class="text-left player-column">Player</th>

        <template v-if="!showAllLeagues">
          <th class="text-center border-left">
              <div class="column items-center">
<!--                <q-icon name="emoji_events" class="text-amber-8" size="22px" />-->
                <span class="q-mt-xs">1st</span>
              </div>
          </th>

          <th class="text-center border-left">
              <div class="column items-center">
<!--                <q-icon name="military_tech" class="text-blue-grey-4" size="22px" />-->
                <span class="q-mt-xs">2nd</span>
              </div>
          </th>

          <th class="text-center border-left">
              <div class="column items-center">
<!--                <q-icon name="military_tech" class="text-brown-5" size="22px" />-->
                <span class="q-mt-xs">3rd</span>
              </div>
          </th>

          <th class="text-center border-left">
              <div class="column items-center">
<!--                <q-icon name="flag" class="text-red-5" size="22px" />-->
                <span class="q-mt-xs">4th</span>
              </div>
          </th>
        </template>

        <template v-else>
          <template v-for="level in standings.levels" :key="level">
            <th class="text-center level-group-header border-left">
              <div class="column items-center">
                <LeagueLevel badge :level="level" class="q-mb-xs" />
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
            <q-separator class="q-my-sm" />
          </td>
        </tr>

        <tr
          class="leaderboard-row"
          :class="{
            'bg-amber-1': index === 0
          }"
        >

          <!-- Rank (with league level badge) -->
          <td class="text-left q-pl-lg leaderboard-rank-text">
            <div class="row items-center no-wrap q-gutter-x-sm">
              <div
              >
                {{ index + 1 }}
              </div>
              <div
                v-if="bestLeague(row)"
                class="league-dot"
                :style="{
                  color: getHexLeagueColor(bestLeague(row)!),
                  borderColor: getHexLeagueColor(bestLeague(row)!)
                }"
              >
                L{{ bestLeague(row) }}
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
            <td class="text-center border-left">
                <span
                  v-if="getHighestLeagueCounts(row).first > 0"
                  class="text-weight-bold text-primary"
                  style="font-size: 1.1rem"
                >
                  {{ getHighestLeagueCounts(row).first }}
                </span>
                <span v-else class="text-grey-4">-</span>
            </td>

            <!-- 2nd -->
            <td class="text-center border-left">
                <span
                  v-if="getHighestLeagueCounts(row).second > 0"
                  class="text-weight-bold text-grey-8"
                >
                  {{ getHighestLeagueCounts(row).second }}
                </span>
                <span v-else class="text-grey-4">-</span>
            </td>

            <!-- 3rd -->
            <td class="text-center border-left">
                <span
                  v-if="getHighestLeagueCounts(row).third > 0"
                  class="text-weight-bold text-grey-7"
                >
                  {{ getHighestLeagueCounts(row).third }}
                </span>
                <span v-else class="text-grey-4">-</span>
            </td>

            <!-- 4th -->
            <td class="text-center border-left">
                <span
                  v-if="getHighestLeagueCounts(row).fourth > 0"
                  class="text-weight-bold text-grey-6"
                >
                  {{ getHighestLeagueCounts(row).fourth }}
                </span>
                <span v-else class="text-grey-4">-</span>
            </td>
          </template>

          <template v-else>
            <template v-for="level in standings.levels" :key="level">
              <td class="text-center q-px-sm border-left">
                <div class="row justify-center items-center no-wrap">
                  <div class="column items-center pos-num">
                    <span :class="row.per_level[level]?.first ? 'text-weight-bold text-primary' : 'text-grey-4'" style="font-size: 11px">
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
                    <span :class="row.per_level[level]?.third ? 'text-weight-bold text-grey-7' : 'text-grey-4'" style="font-size: 11px">
                      {{ row.per_level[level]?.third || '-' }}
                    </span>
                  </div>
                  <div class="pos-sep"></div>
                  <div class="column items-center pos-num">
                    <span :class="row.per_level[level]?.fourth ? 'text-weight-bold text-grey-6' : 'text-grey-4'" style="font-size: 11px">
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

    <!-- Note -->
    <div class="q-px-lg q-py-sm text-caption text-grey-6" style="border-top: 1px solid rgba(0,0,0,0.05)">
      <div class="row items-center q-gutter-x-xs">
        <q-icon name="info" size="14px" />
        <span>Note: Sorted by best league level (L1 highest) and performance.</span>
      </div>
    </div>
  </div>

  <!-- No data -->
  <div v-else class="column items-center q-pa-xl text-grey-6 leaderboard-empty overflow-auto rounded-borders shadow-2">
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
import LeagueLevel from 'components/season/LeagueLevel.vue';

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
.league-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: white;
  font-size: 9px;
  font-weight: 800;
  border: 1px solid;
  line-height: 1;
}

.leaderboard-row {
  transition: background-color 0.2s ease;
  &:hover {
    background-color: rgba(0, 0, 0, 0.02);
  }
}

.pos-sep {
  width: 1.5px;
  height: 12px;
  background-color: rgba(54, 64, 88, 0.1);
  margin: 0 4px;
}

.pos-num {
  min-width: 14px;
}

.divide-y > tr:not(:first-child) {
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.username-link:hover {
  text-decoration: underline;
  color: var(--q-primary);
}
</style>

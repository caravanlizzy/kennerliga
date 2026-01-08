<template>
  <!-- Loading -->
  <LoadingSpinner v-if="loading" />
  <ErrorDisplay v-if="error" error="error" />

  <!-- Content -->
  <div
    v-else-if="standings"
    class="leaderboard-container"
  >
    <!-- Table -->
    <q-markup-table flat dense separator="none" class="leaderboard-table bg-transparent">
      <thead>
      <tr class="text-uppercase text-grey-6 text-caption text-weight-bold header-row">
        <th class="text-left q-pl-lg" style="width: 40%">Player</th>

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
          <!-- Player -->
          <td class="text-left relative-position q-py-md">
            <div
              v-if="shouldShowGroupHeader(index) && bestLeague(row) !== null"
              class="group-label-container"
            >
               <span class="group-label-text" :class="'text-' + leagueBadgeColor(bestLeague(row)!)">
                 League {{ bestLeague(row) }}
               </span>
            </div>

            <div class="row items-center q-gutter-x-md q-pl-lg">
              <UserAvatar
                :display-username="row.profile_name"
                size="32px"
              />
              <div class="column">
                <div class="row items-center q-gutter-x-xs">
                  <span class="text-subtitle2 text-weight-bold text-grey-9">{{ row.profile_name }}</span>
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

          <!-- 1st -->
        <td class="text-center">
            <q-badge
              v-if="row.totals.first > 0"
              color="amber-1"
              text-color="amber-10"
              class="text-weight-bold"
            >
              {{ row.totals.first }}
            </q-badge>
            <span v-else class="text-grey-4">-</span>
        </td>

        <!-- 2nd -->
        <td class="text-center">
            <q-badge
              v-if="row.totals.second > 0"
              color="blue-grey-1"
              text-color="blue-grey-10"
              class="text-weight-bold"
            >
              {{ row.totals.second }}
            </q-badge>
            <span v-else class="text-grey-4">-</span>
        </td>

        <!-- 3rd -->
        <td class="text-center">
            <q-badge
              v-if="row.totals.third > 0"
              color="brown-1"
              text-color="brown-10"
              class="text-weight-bold"
            >
              {{ row.totals.third }}
            </q-badge>
            <span v-else class="text-grey-4">-</span>
        </td>

        <!-- 4th -->
        <td class="text-center">
            <q-badge
              v-if="row.totals.fourth > 0"
              color="red-1"
              text-color="red-10"
              class="text-weight-bold"
            >
              {{ row.totals.fourth }}
            </q-badge>
            <span v-else class="text-grey-4">-</span>
        </td>
      </tr>
      </template>
      </tbody>
    </q-markup-table>
  </div>

  <!-- No data -->
  <div v-else class="text-caption text-grey-7">No Leaderboard available.</div>
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
  totals: PerLevelCounts;
}
interface LeaderBoardResponse {
  year: number;
  levels: number[];
  standings: PlayerYearStanding[];
}

const standings = ref<LeaderBoardResponse | null>(null);
const loading = ref(false);
const error = ref(false);

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

function totalPoints(row: PlayerYearStanding): number {
  return (row.totals.first * 4) + (row.totals.second * 3) + (row.totals.third * 2) + (row.totals.fourth * 1);
}

function shouldShowGroupHeader(index: number): boolean {
  if (!standings.value || !standings.value.standings[index]) return false;
  if (index === 0) return true;

  const currentBest = bestLeague(standings.value.standings[index]);
  const prevBest = bestLeague(standings.value.standings[index - 1]);

  return currentBest !== prevBest;
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
.leaderboard-container {
  overflow: hidden;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(54, 64, 88, 0.08);
  border-radius: 12px;
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
    transform: scale(1.002);
    z-index: 1;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
  }
}

.top-rank-bg {
  background-color: rgba(255, 249, 230, 0.4);
}

.group-label-container {
  position: absolute;
  left: 12px;
  top: -10px;
  z-index: 10;
  background: white;
  padding: 2px 10px;
  border-radius: 20px;
  border: 1px solid rgba(54, 64, 88, 0.1);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.group-label-text {
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.divide-y tr:last-child {
  border-bottom: none;
}
</style>

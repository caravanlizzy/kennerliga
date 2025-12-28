<template>
  <!-- Loading -->
  <LoadingSpinner v-if="loading" />
  <ErrorDisplay v-if="error" error="error" />

  <!-- Content -->
  <div
    v-else-if="standings"
    class="leaderboard-container bg-white rounded-borders shadow-1"
  >
    <!-- Header -->
    <div class="row items-center justify-between q-pa-md border-bottom">
      <div class="column">
        <div class="text-h6 text-weight-bold">Leaderboard</div>
        <div class="text-caption text-grey-7">Season Performance Summary</div>
      </div>
      <q-chip outline color="primary" icon="event" label="Year {{ standings.year }}" />
    </div>

    <!-- Table -->
    <q-markup-table flat dense separator="none" class="leaderboard-table">
      <thead>
      <tr class="text-uppercase text-grey-7 text-caption">
        <th class="text-left q-pl-lg">Player</th>

        <th class="text-center">
            <div class="column items-center">
              <q-icon name="emoji_events" class="text-amber-8" size="20px" />
              <span class="text-weight-bold">1st</span>
            </div>
        </th>

        <th class="text-center">
            <div class="column items-center">
              <q-icon name="military_tech" class="text-blue-grey-4" size="20px" />
              <span class="text-weight-bold">2nd</span>
            </div>
        </th>

        <th class="text-center">
            <div class="column items-center">
              <q-icon name="military_tech" class="text-brown-5" size="20px" />
              <span class="text-weight-bold">3rd</span>
            </div>
        </th>

        <th class="text-center">
            <div class="column items-center">
              <q-icon name="flag" class="text-red-5" size="20px" />
              <span class="text-weight-bold">4th</span>
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
          <td class="text-left relative-position q-py-sm">
            <div
              v-if="bestLeague(row) !== null"
              class="row-group-line"
              :class="'bg-' + leagueBadgeColor(bestLeague(row)!)"
            ></div>
            <div
              v-if="shouldShowGroupHeader(index) && bestLeague(row) !== null"
              class="group-label-container"
            >
               <span class="group-label-text" :class="'text-' + leagueBadgeColor(bestLeague(row)!)">
                 League {{ bestLeague(row) }}
               </span>
            </div>

            <div class="row items-center q-gutter-x-md q-pl-md">
              <UserAvatar
                :display-username="row.profile_name"
                size="36px"
                shape="squircle"
              />
              <div class="column">
                <span class="text-subtitle2 text-weight-bold">{{ row.profile_name }}</span>
                <span v-if="index === 0" class="text-caption text-amber-9 text-weight-medium">Season Leader</span>
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

<style scoped>
.leaderboard-container {
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.leaderboard-table :deep(thead tr th) {
  height: 64px;
}

.leaderboard-row {
  position: relative;
  transition: background-color 0.2s ease;
}

.leaderboard-row:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.top-rank-bg {
  background-color: #fffbeb; /* amber-50 */
}

.top-rank-bg:hover {
  background-color: #fef3c7; /* amber-100 */
}

.row-group-line {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  opacity: 0.8;
}

.group-label-container {
  position: absolute;
  left: 12px;
  top: -10px;
  z-index: 10;
  background: white;
  padding: 0 4px;
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.group-label-text {
  font-size: 9px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.border-bottom {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.divide-y tr:not(:last-child) {
  border-bottom: 1px solid rgba(0, 0, 0, 0.03);
}
</style>

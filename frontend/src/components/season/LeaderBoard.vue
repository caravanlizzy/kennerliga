<template>
  <!-- Loading -->
  <LoadingSpinner v-if="loading" />
  <ErrorDisplay v-if="error" error="error" />

  <!-- Content -->
  <div
    v-else-if="standings"
    class="bg-white rounded-borders q-pa-sm"
  >
    <!-- Header -->
    <div class="row items-baseline justify-between q-mb-sm">
      <div class="text-subtitle2 text-weight-medium">Leaderboard</div>
      <div class="text-caption text-grey-7">Year {{ standings.year }}</div>
    </div>

    <!-- Table -->
    <q-markup-table flat dense separator="horizontal">
      <thead>
      <tr class="text-uppercase text-weight-bold text-caption">
        <th class="text-left">Player</th>

        <th class="text-center">
            <span class="row items-center justify-center no-wrap q-gutter-x-xs">
              <q-icon name="emoji_events" class="text-amber-8" size="16px" />
              <span>1st</span>
            </span>
        </th>

        <th class="text-center">
            <span class="row items-center justify-center no-wrap q-gutter-x-xs">
              <q-icon name="military_tech" class="text-blue-grey-5" size="16px" />
              <span>2nd</span>
            </span>
        </th>

        <th class="text-center">
            <span class="row items-center justify-center no-wrap q-gutter-x-xs">
              <q-icon name="military_tech" class="text-brown-6" size="16px" />
              <span>3rd</span>
            </span>
        </th>

        <th class="text-center">
            <span class="row items-center justify-center no-wrap q-gutter-x-xs">
              <q-icon name="flag" class="text-red-6" size="16px" />
              <span>4th</span>
            </span>
        </th>
      </tr>
      </thead>

      <tbody>
      <template
        v-for="(row, index) in standings.standings"
        :key="row.player_profile_id"
      >
        <tr
          class="leaderboard-row"
          :class="{
            'bg-amber-1': index === 0,
          }"
        >
          <!-- Player -->
          <td class="text-left relative-position">
            <div
              v-if="bestLeague(row) !== null"
              class="row-group-line"
              :class="'bg-' + leagueBadgeColor(bestLeague(row)!)"
            ></div>
            <div
              v-if="shouldShowGroupHeader(index) && bestLeague(row) !== null"
              class="group-label-line"
            >
               <span class="group-label-text">L{{ bestLeague(row) }}</span>
            </div>
            <div class="text-body2 text-weight-medium q-pl-lg">
              {{ row.profile_name }}
            </div>
          </td>

          <!-- 1st -->
        <td class="text-center">
            <span
              class="text-weight-medium"
              :class="row.totals.first > 0 ? 'text-dark' : 'text-grey-6'"
            >
              {{ row.totals.first }}
            </span>
        </td>

        <!-- 2nd -->
        <td class="text-center">
            <span
              class="text-weight-medium"
              :class="row.totals.second > 0 ? 'text-dark' : 'text-grey-6'"
            >
              {{ row.totals.second }}
            </span>
        </td>

        <!-- 3rd -->
        <td class="text-center">
            <span
              class="text-weight-medium"
              :class="row.totals.third > 0 ? 'text-dark' : 'text-grey-6'"
            >
              {{ row.totals.third }}
            </span>
        </td>

        <!-- 4th -->
        <td class="text-center">
            <span
              class="text-weight-medium"
              :class="row.totals.fourth > 0 ? 'text-dark' : 'text-grey-6'"
            >
              {{ row.totals.fourth }}
            </span>
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
.leaderboard-row {
  position: relative;
}

.row-group-line {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
}

.group-label-line {
  position: absolute;
  left: 6px;
  top: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  pointer-events: none;
  z-index: 1;
}

.group-label-text {
  font-size: 10px;
  font-weight: 900;
  color: #555;
  text-transform: uppercase;
  white-space: nowrap;
}
</style>

<template>
  <!-- Loading -->
  <LoadingSpinner v-if="loading" />
  <ErrorDisplay v-if="error" error="error" />

  <!-- Content -->
  <div v-else-if="standings" class="rounded-borders q-pa-md">
    <!-- Header -->
    <div class="row items-baseline justify-between q-mb-sm">
      <div class="text-subtitle2 text-weight-medium">Leaderboard</div>
      <div class="text-caption text-grey-7">Year {{ standings.year }}</div>
    </div>

    <!-- Table -->
    <q-markup-table flat separator="horizontal" class="text-caption year-matrix bg-white">
      <thead>
      <tr>
        <th class="text-left text-uppercase text-weight-medium q-py-xs q-px-sm">
          Player
        </th>

        <th class="text-center text-grey-6 text-weight-light q-py-xs q-px-sm">
          Highest L
        </th>

        <th class="text-center text-uppercase text-weight-medium q-py-xs q-px-sm">
            <span class="place-head">
              <q-icon name="emoji_events" class="text-amber-8" size="16px" />
              1st
            </span>
        </th>

        <th class="text-center text-uppercase text-weight-medium q-py-xs q-px-sm">
            <span class="place-head">
              <q-icon name="military_tech" class="text-blue-grey-5" size="16px" />
              2nd
            </span>
        </th>

        <th class="text-center text-uppercase text-weight-medium q-py-xs q-px-sm">
            <span class="place-head">
              <q-icon name="military_tech" class="text-brown-6" size="16px" />
              3rd
            </span>
        </th>

        <th class="text-center text-uppercase text-weight-medium q-py-xs q-px-sm">
            <span class="place-head">
              <q-icon name="flag" class="text-red-6" size="16px" />
              4th
            </span>
        </th>
      </tr>
      </thead>

      <tbody>
      <tr
        v-for="(row, index) in standings.standings"
        :key="row.player_profile_id"
        :class="[{ 'bg-yellow-1': index === 0 }]"
      >
        <!-- Player -->
        <td class="text-left q-py-xs q-px-sm">
          <div class="text-body2 text-weight-medium">
            {{ row.profile_name }}
          </div>
        </td>

        <!-- Highest league -->
        <td class="text-center q-py-xs q-px-sm">
          <q-badge v-if="bestLeague(row)" class="text-body2 text-weight-medium">
            L{{ bestLeague(row) }}
          </q-badge>
          <div v-else class="text-grey-5 text-caption">–</div>
        </td>

        <!-- 1st -->
        <td class="text-center q-py-xs q-px-sm">
          <div
            v-if="row.totals.first > 0"
            class="text-body2 text-positive text-weight-medium place-cell"
          >
            <span>{{ row.totals.first }}</span>
          </div>
          <div v-else class="text-grey-5 text-caption">0</div>
        </td>

        <!-- 2nd -->
        <td class="text-center q-py-xs q-px-sm">
          <div
            v-if="row.totals.second > 0"
            class="text-body2 text-dark text-weight-medium place-cell"
          >
            <span>{{ row.totals.second }}</span>
          </div>
          <div v-else class="text-grey-5 text-caption">0</div>
        </td>

        <!-- 3rd -->
        <td class="text-center q-py-xs q-px-sm">
          <div
            v-if="row.totals.third > 0"
            class="text-body2 text-accent text-weight-medium place-cell"
          >
            <span>{{ row.totals.third }}</span>
          </div>
          <div v-else class="text-grey-5 text-caption">0</div>
        </td>

        <!-- 4th -->
        <td class="text-center q-py-xs q-px-sm">
          <div
            v-if="row.totals.fourth > 0"
            class="text-body2 text-negative text-weight-medium place-cell"
          >
            <span>{{ row.totals.fourth }}</span>
          </div>
          <div v-else class="text-grey-5 text-caption">0</div>
        </td>
      </tr>
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

watch(
  () => props.year,
  () => fetchStandings(),
  { immediate: true }
);
</script>

<style scoped>
.year-matrix tbody tr:hover {
  background: rgba(0, 0, 0, 0.03);
}

.place-head {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.place-cell {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
</style>

<template>
  <!-- Loading -->
  <LoadingSpinner v-if="loading" />

  <!-- Error -->
  <div
    v-else-if="error"
    class="column items-center q-pa-md bg-white rounded-borders"
  >
    <q-icon name="error_outline" size="22px" color="negative" />
    <span class="q-mt-xs text-negative text-body2">
      Error loading yearly standings
    </span>
    <q-btn
      outline
      color="primary"
      label="Retry"
      size="sm"
      class="q-mt-sm"
      @click="fetchStandings"
    />
  </div>

  <!-- Content -->
  <div
    v-else-if="standings"
    class="year-standings bg-white rounded-borders q-pa-sm"
  >
    <!-- Header -->
    <div class="row items-baseline justify-between q-mb-sm">
      <div class="text-subtitle2 text-weight-medium">
        Yearly standings matrix
      </div>
      <div class="text-caption text-grey-7">
        Year {{ standings.year }}
      </div>
    </div>

    <!-- Table -->
    <q-markup-table
      flat
      separator="horizontal"
      class="text-caption year-matrix bg-white"
    >
      <thead>
      <tr>
        <th class="text-left text-uppercase text-weight-medium q-py-xs q-px-sm">
          Player
        </th>

        <th class="text-center text-uppercase text-weight-medium q-py-xs q-px-sm">
          Highest L
        </th>

        <th class="text-center text-uppercase text-weight-medium q-py-xs q-px-sm">
          1st
        </th>

        <th class="text-center text-uppercase text-weight-medium q-py-xs q-px-sm">
          2nd
        </th>

        <th class="text-center text-uppercase text-weight-medium q-py-xs q-px-sm">
          3rd
        </th>

        <th class="text-center text-uppercase text-weight-medium q-py-xs q-px-sm">
          4th
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
          <div v-if="bestLeague(row)" class="text-body2 text-weight-medium">
            L{{ bestLeague(row) }}
          </div>
          <div v-else class="text-grey-5 text-caption">
            –
          </div>
        </td>

        <!-- 1st -->
        <td class="text-center q-py-xs q-px-sm">
          <div
            v-if="row.totals.first > 0"
            class="text-body2 text-positive text-weight-medium"
          >
            {{ row.totals.first }}
          </div>
          <div v-else class="text-grey-5 text-caption">0</div>
        </td>

        <!-- 2nd -->
        <td class="text-center q-py-xs q-px-sm">
          <div
            v-if="row.totals.second > 0"
            class="text-body2 text-primary text-weight-medium"
          >
            {{ row.totals.second }}
          </div>
          <div v-else class="text-grey-5 text-caption">0</div>
        </td>

        <!-- 3rd -->
        <td class="text-center q-py-xs q-px-sm">
          <div
            v-if="row.totals.third > 0"
            class="text-body2 text-accent text-weight-medium"
          >
            {{ row.totals.third }}
          </div>
          <div v-else class="text-grey-5 text-caption">0</div>
        </td>

        <!-- 4th -->
        <td class="text-center q-py-xs q-px-sm">
          <div
            v-if="row.totals.fourth > 0"
            class="text-body2 text-negative text-weight-medium"
          >
            {{ row.totals.fourth }}
          </div>
          <div v-else class="text-grey-5 text-caption">0</div>
        </td>
      </tr>
      </tbody>
    </q-markup-table>
  </div>

  <!-- No data -->
  <div v-else class="text-caption text-grey-7">
    No standings available.
  </div>
</template>

<script setup lang="ts">
import { api } from 'boot/axios';
import { ref, watch } from 'vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';

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

interface YearMatrixResponse {
  year: number;
  levels: number[];
  standings: PlayerYearStanding[];
}

const standings = ref<YearMatrixResponse | null>(null);
const loading = ref(false);
const error = ref(false);

async function fetchStandings(): Promise<void> {
  loading.value = true;
  error.value = false;
  standings.value = null;

  try {
    const { data } = await api.get<YearMatrixResponse>(
      `year-standings/?year=${props.year}`
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
</style>

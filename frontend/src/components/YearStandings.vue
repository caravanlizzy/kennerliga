<template>
  <!-- Loading -->
  <LoadingSpinner v-if="loading" />

  <!-- Error -->
  <div
    v-else-if="error"
    class="column items-center q-pa-md bg-white rounded-borders"
  >
    <q-icon name="error_outline" size="24px" color="negative" />
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
    class="year-standings bg-white rounded-borders q-pa-md"
  >
    <!-- Header row -->
    <div class="row items-baseline justify-between q-mb-md">
      <div class="text-subtitle1 text-weight-medium">
        Yearly standings matrix
      </div>
      <div class="text-body2 text-grey-7">
        Year {{ standings.year }}
      </div>
    </div>

    <!-- Table -->
    <q-markup-table
      flat
      separator="horizontal"
      class="text-body2 year-matrix"
    >
      <thead>
      <tr>
        <th class="text-left text-uppercase text-weight-medium q-py-sm q-px-md">
          Player
        </th>
        <th class="text-center text-uppercase text-weight-medium q-py-sm q-px-md">
          Highest league
        </th>
        <th class="text-center text-uppercase text-weight-medium q-py-sm q-px-md">
          1st place
        </th>
        <th class="text-center text-uppercase text-weight-medium q-py-sm q-px-md">
          2nd place
        </th>
        <th class="text-center text-uppercase text-weight-medium q-py-sm q-px-md">
          3rd place
        </th>
        <th class="text-center text-uppercase text-weight-medium q-py-sm q-px-md">
          4th place
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
        <td class="text-left q-py-sm q-px-md">
          <div class="text-body1 text-weight-medium">
            {{ row.profile_name }}
          </div>
        </td>

        <!-- Highest league (explicit) -->
        <td class="text-center q-py-sm q-px-md">
          <div v-if="bestLeague(row)" class="text-body2 text-weight-medium">
            L{{ bestLeague(row) }}
          </div>
          <div v-else class="text-grey-5 text-body2">
            –
          </div>
        </td>

        <!-- 1st -->
        <td class="text-center q-py-sm q-px-md">
          <div
            v-if="row.totals.first > 0"
            class="text-body1 text-positive text-weight-bold"
          >
            {{ row.totals.first }}
          </div>
          <div v-else class="text-grey-5 text-body2">
            0
          </div>
        </td>

        <!-- 2nd -->
        <td class="text-center q-py-sm q-px-md">
          <div
            v-if="row.totals.second > 0"
            class="text-body1 text-primary text-weight-bold"
          >
            {{ row.totals.second }}
          </div>
          <div v-else class="text-grey-5 text-body2">
            0
          </div>
        </td>

        <!-- 3rd -->
        <td class="text-center q-py-sm q-px-md">
          <div
            v-if="row.totals.third > 0"
            class="text-body1 text-accent text-weight-bold"
          >
            {{ row.totals.third }}
          </div>
          <div v-else class="text-grey-5 text-body2">
            0
          </div>
        </td>

        <!-- 4th (worst) -->
        <td class="text-center q-py-sm q-px-md">
          <div
            v-if="row.totals.fourth > 0"
            class="text-body1 text-negative text-weight-bold"
          >
            {{ row.totals.fourth }}
          </div>
          <div v-else class="text-grey-5 text-body2">
            0
          </div>
        </td>
      </tr>
      </tbody>
    </q-markup-table>
  </div>

  <!-- No data, no error -->
  <div v-else class="text-body2 text-grey-7">
    No standings available.
  </div>
</template>

<script setup lang="ts">
import { api } from 'boot/axios';
import { ref, watch } from 'vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';

const props = defineProps<{
  year: number;
}>();

type PositionKey = 'first' | 'second' | 'third' | 'fourth';

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
    console.error('Error fetching yearly standings:', e);
    error.value = true;
  } finally {
    loading.value = false;
  }
}

/**
 * Highest (best) league level where the player has *any* placements.
 * Lower number = better league (L1 > L2).
 */
function bestLeague(row: PlayerYearStanding): number | null {
  const levelsWithResults: number[] = [];

  for (const [levelKey, counts] of Object.entries(row.per_level || {})) {
    const c = counts as PerLevelCounts;
    if (c.first || c.second || c.third || c.fourth) {
      levelsWithResults.push(Number(levelKey));
    }
  }

  if (levelsWithResults.length === 0) return null;
  return Math.min(...levelsWithResults);
}

// fetch once and whenever year changes
watch(
  () => props.year,
  () => {
    fetchStandings();
  },
  { immediate: true }
);
</script>

<style scoped>
.year-standings {
  width: 100%;
}

.year-matrix tbody tr:hover {
  background: rgba(0, 0, 0, 0.03);
}
</style>

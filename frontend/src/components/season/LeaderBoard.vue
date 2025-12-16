<template>
  <!-- Loading -->
  <LoadingSpinner v-if="loading" />
  <ErrorDisplay v-if="error" error="error" />

  <!-- Content -->
  <div v-else-if="standings" class="leaderboard">
    <!-- Header -->
    <div class="leaderboard__header">
      <div class="leaderboard__title">Leaderboard</div>
      <div class="leaderboard__meta">Year {{ standings.year }}</div>
    </div>

    <!-- Table -->
    <q-markup-table flat separator="horizontal" class="leaderboard__table">
      <thead>
      <tr>
        <th class="th th--player">Player</th>

        <th class="th th--place">
            <span class="place-head">
              <q-icon name="emoji_events" class="text-amber-8" size="16px" />
              1st
            </span>
        </th>

        <th class="th th--place">
            <span class="place-head">
              <q-icon name="military_tech" class="text-blue-grey-5" size="16px" />
              2nd
            </span>
        </th>

        <th class="th th--place">
            <span class="place-head">
              <q-icon name="military_tech" class="text-brown-6" size="16px" />
              3rd
            </span>
        </th>

        <th class="th th--place">
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
        class="leaderboard__row"
        :class="{ 'leaderboard__row--top': index === 0 }"
      >
        <!-- Player -->
        <td class="td td--player">
          <div class="player-name">
            {{ row.profile_name }}
          </div>

          <!-- Floating badge: positioned relative to the whole row (not a column) -->
          <q-badge
            v-if="bestLeague(row) !== null"
            outline
            color="primary"
            class="best-league-badge"
          >
            L{{ bestLeague(row) }}
          </q-badge>
        </td>

        <!-- 1st -->
        <td class="td td--place">
          <div v-if="row.totals.first > 0" class="place place--pos">
            {{ row.totals.first }}
          </div>
          <div v-else class="place place--zero">0</div>
        </td>

        <!-- 2nd -->
        <td class="td td--place">
          <div v-if="row.totals.second > 0" class="place place--dark">
            {{ row.totals.second }}
          </div>
          <div v-else class="place place--zero">0</div>
        </td>

        <!-- 3rd -->
        <td class="td td--place">
          <div v-if="row.totals.third > 0" class="place place--accent">
            {{ row.totals.third }}
          </div>
          <div v-else class="place place--zero">0</div>
        </td>

        <!-- 4th -->
        <td class="td td--place">
          <div v-if="row.totals.fourth > 0" class="place place--neg">
            {{ row.totals.fourth }}
          </div>
          <div v-else class="place place--zero">0</div>
        </td>
      </tr>
      </tbody>
    </q-markup-table>
  </div>

  <!-- No data -->
  <div v-else class="leaderboard__empty">No Leaderboard available.</div>
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
.leaderboard {
  background: #fff;
  border-radius: 8px;
  padding: 12px;
}

.leaderboard__header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 8px;
}

.leaderboard__title {
  font-size: 14px;
  font-weight: 600;
}

.leaderboard__meta {
  font-size: 12px;
  color: #6b7280;
}

.leaderboard__table {
  font-size: 12px;
}

.th,
.td {
  padding: 6px 8px;
  vertical-align: middle;
  white-space: nowrap;
}

.th {
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.th--player,
.td--player {
  text-align: left;
  width: 100%;
  white-space: normal;
}

.th--place,
.td--place {
  text-align: center;
  width: 64px;
}

.leaderboard__row {
  position: relative; /* anchor for floating badge */
}

.leaderboard__row:hover {
  background: rgba(0, 0, 0, 0.03);
}

.leaderboard__row--top {
  background: #fff9c4;
}

.player-name {
  font-size: 14px;
  font-weight: 600;
  line-height: 1.2;
}

/* This is the key: badge floats over the row, not inside a "column" */
.best-league-badge {
  position: absolute;
  top: 50%;
  right: 8px;
  transform: translateY(-50%);
  font-size: 11px;
  border-radius: 999px;
  padding: 2px 8px;
  pointer-events: none; /* avoids interfering with row hover/clicks */
}

.place-head {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.place {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  font-weight: 600;
}

.place--zero {
  color: #9ca3af;
  font-weight: 500;
}

.place--pos {
  color: #16a34a;
}

.place--dark {
  color: #111827;
}

.place--accent {
  color: #7c3aed;
}

.place--neg {
  color: #dc2626;
}

.leaderboard__empty {
  font-size: 12px;
  color: #6b7280;
}
</style>

<template>
  <q-page
    class="max-width-container q-mx-auto game-detail-page"
    :class="isMobile ? 'q-pa-sm' : 'q-pa-md'"
  >
    <!-- Loading State -->
    <div v-if="loading" class="q-py-xl text-center">
      <LoadingSpinner />
    </div>

    <!-- Error State -->
    <div v-else-if="error || !stats" class="q-py-md">
      <q-banner rounded dense class="bg-red-1 text-negative q-mb-md">
        <template #avatar><q-icon name="warning" color="negative" /></template>
        {{ error || 'Game details could not be loaded.' }}
      </q-banner>
      <KennerButton
        outline
        no-caps
        icon="arrow_back"
        label="Back to Statistics"
        @click="router.push({ name: 'statistics' })"
      />
    </div>

    <!-- Main Content -->
    <div
      v-else
      class="column"
      :class="isMobile ? 'q-gutter-y-sm' : 'q-gutter-y-lg'"
    >
      <!-- Header & Hero Section Component -->
      <GameHeroHeader
        :game="stats.game"
        :is-admin="isAdmin"
        :available-player-counts="availablePlayerCounts"
        :selected-player-counts="selectedPlayerCounts"
        :is-all-player-counts-selected="isAllPlayerCountsSelected"
        :selected-years="selectedYears"
        :year-options="yearOptions"
        :years-display-value="yearsDisplayValue"
        @back="router.push({ name: 'statistics' })"
        @view-config="
          router.push({
            name: 'game-config',
            params: { id: $event },
          })
        "
        @edit-game="
          router.push({
            name: 'game-edit',
            params: { id: $event },
          })
        "
        @toggle-player-count="togglePlayerCount"
        @toggle-all-player-counts="toggleAllPlayerCounts"
        @update:selected-years="selectedYears = $event"
      />

      <!-- KPI Summary Cards Grid Component -->
      <GameKpiGrid
        :stats="stats"
        :top-player="topPlayer"
        @view-match="
          router.push({ name: 'match-detail', params: { id: $event } })
        "
      />

      <!-- Navigation Tabs & Panels -->
      <div>
        <q-tabs
          v-model="activeTab"
          dense
          no-caps
          align="left"
          active-color="primary"
          indicator-color="primary"
          class="text-grey-7 border-bottom"
          :class="isMobile ? 'q-mb-sm' : 'q-mb-md'"
        >
          <q-tab
            name="leaderboard"
            label="Player Standings"
            icon="leaderboard"
          />
          <q-tab
            name="matches"
            label="Match History"
            icon="history"
            :badge="stats.matches ? String(stats.matches.length) : undefined"
          />
          <q-tab
            v-if="hasFactionsOrRules"
            name="factions"
            label="Factions &amp; Rules"
            icon="tune"
          />
        </q-tabs>

        <q-tab-panels
          v-model="activeTab"
          animated
          keep-alive
          class="bg-transparent"
        >
          <!-- Leaderboard Panel -->
          <q-tab-panel name="leaderboard" class="q-pa-none">
            <GameLeaderboardCard
              :leaderboard="stats.leaderboard"
              :columns="leaderboardColumns"
            />
          </q-tab-panel>

          <!-- Match History Panel -->
          <q-tab-panel name="matches" class="q-pa-none">
            <GameMatchHistoryCard
              :matches="stats.matches"
              :format-date="formatDate"
              @view-match="
                router.push({ name: 'match-detail', params: { id: $event } })
              "
            />
          </q-tab-panel>

          <!-- Factions & Rules Panel -->
          <q-tab-panel
            v-if="hasFactionsOrRules"
            name="factions"
            class="q-pa-none"
          >
            <GameFactionStatsCard
              :factions="stats.factions"
              :columns="factionColumns"
              :game="stats.game"
              :is-admin="isAdmin"
              @edit-config="
                router.push({
                  name: 'game-config',
                  params: { id: $event },
                })
              "
            />
          </q-tab-panel>
        </q-tab-panels>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from 'src/stores/userStore';
import { fetchGameDetailedStatistics } from 'src/services/statisticsService';
import {
  TGameDetailedStatistics,
  TGameFactionStat,
  TGameLeaderboardPlayer,
} from 'src/types';
import KennerButton from 'components/base/KennerButton.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import GameHeroHeader from 'components/game/detail/GameHeroHeader.vue';
import GameKpiGrid from 'components/game/detail/GameKpiGrid.vue';
import GameLeaderboardCard from 'components/game/detail/GameLeaderboardCard.vue';
import GameMatchHistoryCard from 'components/game/detail/GameMatchHistoryCard.vue';
import GameFactionStatsCard from 'components/game/detail/GameFactionStatsCard.vue';
import { useResponsive } from 'src/composables/responsive';

const { isMobile } = useResponsive();
const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const isAdmin = computed(() => userStore.isAdmin);

const loading = ref(true);
const error = ref<string | null>(null);
const stats = ref<TGameDetailedStatistics | null>(null);

const activeTab = ref<'leaderboard' | 'matches' | 'factions'>('leaderboard');

// Filters
const selectedYears = ref<number[]>([]);
const selectedPlayerCounts = ref<string[]>([]);
const availablePlayerCounts = ['2p', '3p', '4p', '5p', '6p'];

const yearOptions = [
  { label: '2026', value: 2026 },
  { label: '2025', value: 2025 },
];

const isAllPlayerCountsSelected = computed(
  () => selectedPlayerCounts.value.length === 0
);

function toggleAllPlayerCounts() {
  selectedPlayerCounts.value = [];
}

function togglePlayerCount(count: string) {
  const index = selectedPlayerCounts.value.indexOf(count);
  if (index === -1) {
    selectedPlayerCounts.value.push(count);
  } else {
    selectedPlayerCounts.value.splice(index, 1);
  }
}

const yearsDisplayValue = computed(() => {
  if (selectedYears.value.length === 0) return 'All Years';
  return selectedYears.value.join(', ');
});

const topPlayer = computed<TGameLeaderboardPlayer | null>(() => {
  if (!stats.value?.leaderboard || stats.value.leaderboard.length === 0) {
    return null;
  }
  return stats.value.leaderboard[0];
});

const hasFactionsOrRules = computed(() => {
  return (
    (stats.value?.factions && stats.value.factions.length > 0) ||
    Boolean(stats.value?.game.options && stats.value.game.options.length > 0) ||
    Boolean(stats.value?.game.is_asymmetric)
  );
});

async function loadData() {
  const gameId = Number(route.params.id);
  if (!gameId || isNaN(gameId)) {
    error.value = 'Invalid game id';
    loading.value = false;
    return;
  }
  try {
    loading.value = true;
    error.value = null;
    const data = await fetchGameDetailedStatistics(
      gameId,
      selectedYears.value,
      selectedPlayerCounts.value,
      0
    );
    if (!data) {
      error.value = 'Game not found';
    } else {
      stats.value = data;
    }
  } catch (e: any) {
    error.value = e?.message || 'Could not load game statistics';
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadData();
});

watch(
  [selectedYears, selectedPlayerCounts],
  () => {
    loadData();
  },
  { deep: true }
);

watch(
  () => route.params.id,
  (newId) => {
    if (newId) loadData();
  }
);

function formatDate(dateStr?: string) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

// Columns definition for Leaderboard
const leaderboardColumns = [
  {
    name: 'rank',
    label: 'Rank',
    field: (r: TGameLeaderboardPlayer) => r.rank,
    align: 'center',
    sortable: true,
  },
  {
    name: 'profile_name',
    label: 'Player',
    field: (r: TGameLeaderboardPlayer) => r.profile_name,
    align: 'left',
    sortable: true,
  },
  {
    name: 'win_rate',
    label: 'Win Rate',
    field: (r: TGameLeaderboardPlayer) => r.win_rate,
    align: 'left',
    sortable: true,
  },
  {
    name: 'games_played',
    label: 'Matches',
    field: (r: TGameLeaderboardPlayer) => `${r.wins} / ${r.games_played}`,
    align: 'center',
    sortable: true,
  },
  {
    name: 'avg_position',
    label: 'Avg Position',
    field: (r: TGameLeaderboardPlayer) =>
      r.avg_position !== null ? r.avg_position : '-',
    align: 'center',
    sortable: true,
  },
  {
    name: 'best_score',
    label: 'Best Score',
    field: (r: TGameLeaderboardPlayer) =>
      r.best_score !== null ? r.best_score : '-',
    align: 'center',
    sortable: true,
  },
  {
    name: 'avg_score',
    label: 'Avg Score',
    field: (r: TGameLeaderboardPlayer) =>
      r.avg_score !== null ? r.avg_score : '-',
    align: 'center',
    sortable: true,
  },
];

// Columns definition for Factions
const factionColumns = [
  {
    name: 'name',
    label: 'Faction',
    field: (r: TGameFactionStat) => r.name,
    align: 'left',
    sortable: true,
  },
  {
    name: 'games_played',
    label: 'Plays',
    field: (r: TGameFactionStat) => r.games_played,
    align: 'center',
    sortable: true,
  },
  {
    name: 'wins',
    label: 'Wins',
    field: (r: TGameFactionStat) => r.wins,
    align: 'center',
    sortable: true,
  },
  {
    name: 'win_rate',
    label: 'Win Rate',
    field: (r: TGameFactionStat) => r.win_rate,
    align: 'center',
    sortable: true,
  },
  {
    name: 'avg_position',
    label: 'Avg Position',
    field: (r: TGameFactionStat) =>
      r.avg_position !== null ? r.avg_position : '-',
    align: 'center',
    sortable: true,
  },
  {
    name: 'avg_points',
    label: 'Avg Points',
    field: (r: TGameFactionStat) =>
      r.avg_points !== null ? r.avg_points : '-',
    align: 'center',
    sortable: true,
  },
  {
    name: 'best_score',
    label: 'Best Score',
    field: (r: TGameFactionStat) =>
      r.best_score !== null ? r.best_score : '-',
    align: 'center',
    sortable: true,
  },
];
</script>

<style scoped lang="scss">
.game-detail-page {
  max-width: 1200px;
}

.border-bottom {
  border-bottom: 1px solid var(--kenner-border-subtle, rgba(0, 0, 0, 0.08));
}
</style>

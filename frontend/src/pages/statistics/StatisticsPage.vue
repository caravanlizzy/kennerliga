<template>
  <q-page class="q-pa-md max-width-container q-mx-auto statistics-page">
    <div class="q-mb-md">
      <div class="row items-center q-gutter-x-sm q-mb-sm">
        <div class="stat-icon-box stat-icon-box--lg">
          <q-icon name="query_stats" color="primary" size="24px" />
        </div>
        <div class="text-body2 text-grey-7">Rankings, records &amp; leaderboards.</div>
      </div>

      <!-- Full width and stacked on mobile so the chips/select never wrap
           into each other; inline once there's room (col-sm-auto). -->
      <div class="row q-col-gutter-sm items-center filters-row">
        <div class="col-12 col-sm-auto">
          <!-- Player-count filter, mirroring the chips on the players list. -->
          <div class="row items-center q-gutter-x-sm">
            <div class="row items-center text-caption text-weight-bold text-grey-8">
              <q-icon name="groups" size="18px" class="q-mr-xs text-primary" />
              <span>Players:</span>
            </div>
            <div class="row q-gutter-xs items-center">
              <q-chip
                clickable
                dense
                :outline="!isAllPlayerCountsSelected"
                :color="isAllPlayerCountsSelected ? 'primary' : 'grey-7'"
                text-color="white"
                size="sm"
                class="text-weight-bold"
                style="border-radius: 4px"
                @click="toggleAllPlayerCounts"
              >
                All
              </q-chip>
              <q-chip
                v-for="pc in availablePlayerCounts"
                :key="pc"
                clickable
                dense
                :outline="!selectedPlayerCounts.includes(pc)"
                :color="selectedPlayerCounts.includes(pc) ? 'primary' : 'grey-7'"
                text-color="white"
                size="sm"
                class="text-weight-bold"
                style="border-radius: 4px"
                @click="togglePlayerCount(pc)"
              >
                {{ pc.toUpperCase() }}
              </q-chip>
            </div>
          </div>
        </div>

        <div class="col-12 col-sm-auto years-filter" style="min-width: 180px">
          <KennerSelect
            v-model="selectedYears"
            :options="yearOptions"
            label="Years"
            multiple
            clearable
            dense
            :display-value="yearsDisplayValue"
          />
        </div>
      </div>
    </div>

    <!-- Split layout: ranking categories on the left, the per-game
         leaderboard pinned top-right so it is visible without scrolling
         past all the category cards first. -->
    <div class="row q-col-gutter-md">
      <div class="col-12 col-md-7 order-last order-md-first">
        <div v-if="loadingOverview" class="row q-col-gutter-md">
          <div v-for="i in 6" :key="i" class="col-12 col-sm-6">
            <q-skeleton type="rect" height="240px" class="rounded-borders" />
          </div>
        </div>

        <div v-else class="row q-col-gutter-md">
          <div v-for="award in overview?.awards ?? []" :key="award.key" class="col-12 col-sm-6">
            <StatCategoryCard :category="award" />
          </div>
          <div
            v-for="category in overview?.categories ?? []"
            :key="category.key"
            class="col-12 col-sm-6"
          >
            <StatCategoryCard :category="category" />
          </div>
        </div>
      </div>

      <div class="col-12 col-md-5 order-first order-md-last">
        <q-card flat bordered class="game-stats-card">
      <q-card-section class="q-pb-sm">
        <div class="row items-center no-wrap">
          <div class="stat-icon-box q-mr-sm">
            <q-icon name="sports_esports" color="primary" size="22px" />
          </div>
          <div class="column">
            <div class="text-subtitle1 text-weight-bolder text-dark line-height-1">Game Stats</div>
            <div class="text-caption text-grey-6">Search for a game to see who performs best at it.</div>
          </div>
        </div>
      </q-card-section>

      <q-separator class="q-mx-md" />

      <q-card-section>
        <q-input
          v-model="gameSearch"
          label="Search games"
          clearable
          dense
          outlined
          class="q-mb-md"
        >
          <template v-slot:prepend>
            <q-icon name="search" />
          </template>
        </q-input>

        <div class="game-preview-list q-mb-md">
          <div
            v-for="game in filteredGames"
            :key="game.game_id"
            class="game-preview-row row items-center justify-between no-wrap"
            :class="{ 'game-preview-row--active': game.game_id === selectedGameId }"
            @click="selectedGameId = selectedGameId === game.game_id ? null : game.game_id"
          >
            <div class="game-preview-row__name ellipsis text-weight-bold">{{ game.name }}</div>
            <div v-if="game.best_player" class="game-preview-row__best text-caption ellipsis">
              <q-icon name="emoji_events" size="14px" class="text-amber-8 q-mr-xs" />
              {{ game.best_player.profile_name }}
              <span v-if="game.best_player.win_rate !== null" class="text-grey-6">
                &middot; {{ game.best_player.win_rate }}%
              </span>
            </div>
            <div v-else class="text-caption text-grey-5">No ranked player</div>
          </div>
          <div v-if="filteredGames.length === 0" class="text-caption text-grey-6 q-pa-sm">
            No games match that search.
          </div>
        </div>

        <!-- Desktop/tablet: the leaderboard expands inline, right below the
             game list, since the sticky column gives it room to breathe. -->
        <template v-if="!smallScreen">
          <GameLeaderboardPanel
            v-if="selectedGameId !== null"
            :loading="loadingLeaderboard"
            :leaderboard="leaderboard"
            :fame-leaders="fameLeaders"
            :columns="gameLeaderboardColumns"
          />
          <div v-else class="text-caption text-grey-6 q-pa-md">
            Pick a game above to see its full leaderboard.
          </div>
        </template>
      </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Mobile: a maximized dialog instead of an inline panel -- avoids the
         nested-scrolling mess of a growing field inside an already-scrolling
         page. -->
    <q-dialog
      v-model="mobileLeaderboardOpen"
      maximized
      transition-show="slide-up"
      transition-hide="slide-down"
    >
      <q-card class="mobile-leaderboard-card">
        <div class="mobile-leaderboard-header row items-center no-wrap">
          <q-icon name="emoji_events" size="22px" color="white" class="q-mr-sm" />
          <div class="text-subtitle1 text-weight-bolder text-white ellipsis">
            {{ selectedGame?.name ?? 'Leaderboard' }}
          </div>
          <q-space />
          <q-btn flat round dense icon="close" color="white" v-close-popup />
        </div>
        <q-card-section class="mobile-leaderboard-body">
          <GameLeaderboardPanel
            :loading="loadingLeaderboard"
            :leaderboard="leaderboard"
            :fame-leaders="fameLeaders"
            :columns="gameLeaderboardColumns"
          />
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
defineOptions({ name: 'StatisticsPage' });

import { computed, onMounted, ref, watch } from 'vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import StatCategoryCard from 'components/statistics/StatCategoryCard.vue';
import GameLeaderboardPanel from 'components/statistics/GameLeaderboardPanel.vue';
import { useResponsive } from 'src/composables/responsive';
import { useUserStore } from 'stores/userStore';
import {
  fetchGameLeaderboard,
  fetchGameStatsList,
  fetchStatisticsOverview,
} from 'src/services/statisticsService';
import { TGameLeaderboard, TGameStatSummary, TStatisticsOverview } from 'src/types';

const { getAvailableYears } = useUserStore();
// Same breakpoint the layout already stacks at (col-md-*), so the dialog
// takes over exactly when the two-column split collapses into one.
const { smallScreen } = useResponsive();

const selectedYears = ref<number[]>([]);
const yearOptions = ref<number[]>([]);
const yearsDisplayValue = computed(() =>
  selectedYears.value.length === 0
    ? 'All Time'
    : selectedYears.value.slice().sort((a, b) => b - a).join(', ')
);

// Player-count filter, mirroring UsersListPage: default to 4P, empty means
// "All". A backend-friendly value (undefined when All) is derived below.
const availablePlayerCounts = ['2p', '3p', '4p'];
const selectedPlayerCounts = ref<string[]>(['4p']);
const isAllPlayerCountsSelected = computed(() => selectedPlayerCounts.value.length === 0);
const playerCountsParam = computed(() =>
  selectedPlayerCounts.value.length > 0 ? selectedPlayerCounts.value : undefined
);

function togglePlayerCount(val: string) {
  const idx = selectedPlayerCounts.value.indexOf(val);
  if (idx >= 0) {
    selectedPlayerCounts.value.splice(idx, 1);
  } else {
    selectedPlayerCounts.value.push(val);
  }
  // If every individual count is selected, collapse to "All" (empty array).
  if (selectedPlayerCounts.value.length === availablePlayerCounts.length) {
    selectedPlayerCounts.value = [];
  }
}

function toggleAllPlayerCounts() {
  selectedPlayerCounts.value = [];
}

const overview = ref<TStatisticsOverview | null>(null);
const loadingOverview = ref(false);

const allGames = ref<TGameStatSummary[]>([]);
const gameSearch = ref('');
const filteredGames = computed(() => {
  const needle = gameSearch.value.trim().toLowerCase();
  if (!needle) return allGames.value;
  return allGames.value.filter((game) => game.name.toLowerCase().includes(needle));
});

const selectedGameId = ref<number | null>(null);
const selectedGame = computed(
  () => allGames.value.find((game) => game.game_id === selectedGameId.value) ?? null
);
const leaderboard = ref<TGameLeaderboard | null>(null);
const loadingLeaderboard = ref(false);

const mobileLeaderboardOpen = computed({
  get: () => smallScreen.value && selectedGameId.value !== null,
  set: (open: boolean) => {
    if (!open) selectedGameId.value = null;
  },
});

// The three most dominant players at the selected game, ranked by win rate.
const fameLeaders = computed(() => {
  if (!leaderboard.value) return [];
  return leaderboard.value.leaderboard
    .filter((entry) => entry.eligible && entry.win_rate !== null)
    .map((entry) => ({
      ...entry,
      fameScore: entry.win_rate as number,
    }))
    .sort((a, b) => b.fameScore - a.fameScore)
    .slice(0, 3);
});

async function loadOverview() {
  loadingOverview.value = true;
  try {
    overview.value = await fetchStatisticsOverview({
      years: selectedYears.value,
      playerCounts: playerCountsParam.value,
      // Large enough to cover every player in any realistic league, so the
      // category cards' "show all" expansion never needs a second request.
      topN: 200,
    });
  } finally {
    loadingOverview.value = false;
  }
}

async function loadGames() {
  allGames.value = await fetchGameStatsList(selectedYears.value, playerCountsParam.value);
}

async function loadLeaderboard() {
  if (selectedGameId.value === null) {
    leaderboard.value = null;
    return;
  }
  loadingLeaderboard.value = true;
  try {
    leaderboard.value = await fetchGameLeaderboard(
      selectedGameId.value,
      selectedYears.value,
      playerCountsParam.value
    );
  } finally {
    loadingLeaderboard.value = false;
  }
}

watch(
  [selectedYears, selectedPlayerCounts],
  () => {
    void loadOverview();
    void loadGames();
    void loadLeaderboard();
  },
  { deep: true }
);

watch(selectedGameId, () => {
  void loadLeaderboard();
});

onMounted(async () => {
  const years = await getAvailableYears();
  yearOptions.value = years ?? [];
  await Promise.all([loadOverview(), loadGames()]);
});

const gameLeaderboardColumns = [
  {
    name: 'rank',
    label: '#',
    align: 'left',
    field: (row: { rank: number | null }) => row.rank,
    format: (val: number | null) => (val !== null ? `${val}` : '-'),
    sortable: true,
  },
  {
    name: 'profile_name',
    label: 'Player',
    align: 'left',
    field: (row: { profile_name: string }) => row.profile_name,
    sortable: true,
  },
  {
    name: 'games_played',
    label: 'Games',
    align: 'right',
    field: (row: { games_played: number }) => row.games_played,
    sortable: true,
  },
  {
    name: 'win_rate',
    label: 'Win %',
    align: 'right',
    field: (row: { win_rate: number | null }) => row.win_rate,
    format: (val: number | null) => (val !== null ? `${val.toFixed(1)}%` : '-'),
    sortable: true,
  },
  {
    name: 'avg_position',
    label: 'Avg Pos',
    align: 'right',
    field: (row: { avg_position: number | null }) => row.avg_position,
    format: (val: number | null) => (val !== null ? val.toFixed(2) : '-'),
    sortable: true,
  },
];
</script>

<style scoped lang="scss">
.stat-icon-box {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(99, 102, 241, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon-box--lg {
  width: 44px;
  height: 44px;
  border-radius: 10px;
}

// KennerSelect's floating label rises above its own box -- once the Years
// filter wraps onto its own line below the player chips (mobile), it needs
// a bit of headroom so the label doesn't sit on top of the chips.
@media (max-width: 599px) {
  .years-filter {
    margin-top: 12px;
  }
}

.game-preview-list {
  max-height: 320px;
  overflow-y: auto;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 8px;

  // Fewer rows in view at once on phones -- easier to scan, with the
  // scrollbar making it obvious there's more below.
  @media (max-width: 599px) {
    max-height: 200px;
  }
}

.game-preview-row {
  padding: 8px 12px;
  cursor: pointer;
  gap: 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  transition: background-color 0.15s ease;

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    background: rgba(99, 102, 241, 0.04);
  }

  &--active {
    background: rgba(99, 102, 241, 0.08);
  }

  &__name {
    min-width: 0;
    flex: 1 1 auto;
  }

  &__best {
    flex: 0 0 auto;
    max-width: 55%;
  }
}

// Keep the per-game panel visible while scrolling the (usually taller)
// column of category cards next to it on wide screens.
@media (min-width: 1024px) {
  .game-stats-card {
    position: sticky;
    top: 16px;
  }
}

.mobile-leaderboard-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  // The app applies a global rounded-corners style to every q-card; a
  // maximized dialog should fill the screen edge to edge instead.
  border-radius: 0 !important;
}

// A trophy-gold gradient rather than the app's indigo accent -- gives the
// mobile leaderboard its own bit of color instead of adding to the purple
// already used everywhere else.
.mobile-leaderboard-header {
  flex: 0 0 auto;
  padding: 14px 16px;
  background: linear-gradient(135deg, #b45309, #f59e0b);
}

.mobile-leaderboard-body {
  flex: 1 1 auto;
  overflow-y: auto;
}
</style>

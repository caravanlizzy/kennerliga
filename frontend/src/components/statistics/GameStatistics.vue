<template>
  <div class="game-statistics">
    <div class="section-header row items-center no-wrap q-mb-md">
      <div class="section-header__icon">
        <q-icon name="sports_esports" color="primary" size="20px" />
      </div>
      <div class="column">
        <div class="text-h6 text-weight-bolder text-dark line-height-1">Games</div>
        <div class="text-caption text-grey-6">
          Which games get played, picked, banned &amp; who masters them.
        </div>
      </div>
    </div>

    <q-skeleton
      v-if="loadingPopular"
      type="rect"
      height="180px"
      class="rounded-borders q-mb-lg"
    />
    <PopularGamesCard
      v-else
      :popular="popular"
      class="q-mb-lg"
      @select="onSelectPopularGame"
    />

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

        <div
          class="game-preview-list q-mb-md"
          :class="{ 'game-preview-list--collapsed': selectedGameId !== null }"
        >
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
          <template v-if="selectedGameId !== null">
            <div class="selected-game-header row items-center justify-between q-mb-sm">
              <div class="text-weight-bolder text-dark ellipsis">{{ selectedGame?.name }}</div>
              <q-btn
                flat
                round
                dense
                size="sm"
                icon="close"
                color="grey-7"
                @click="selectedGameId = null"
              />
            </div>
            <GameLeaderboardPanel
              :loading="loadingLeaderboard"
              :leaderboard="leaderboard"
              :fame-leaders="fameLeaders"
              :columns="gameLeaderboardColumns"
            />
          </template>
          <div v-else class="text-caption text-grey-6 q-pa-md">
            Pick a game above to see its full leaderboard.
          </div>
        </template>
      </q-card-section>
    </q-card>

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
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'GameStatistics' });

import { computed, onMounted, ref, watch } from 'vue';
import GameLeaderboardPanel from 'components/statistics/GameLeaderboardPanel.vue';
import PopularGamesCard from 'components/statistics/PopularGamesCard.vue';
import { useResponsive } from 'src/composables/responsive';
import {
  fetchGameLeaderboard,
  fetchGameStatsList,
  fetchPopularGames,
} from 'src/services/statisticsService';
import { TGameLeaderboard, TGameStatSummary, TPopularGames } from 'src/types';

const props = defineProps<{
  years: number[];
  playerCounts: string[] | undefined;
}>();

// Same breakpoint the layout already stacks at (col-md-*), so the dialog
// takes over exactly when the two-column split collapses into one.
const { smallScreen } = useResponsive();

const popular = ref<TPopularGames | null>(null);
const loadingPopular = ref(false);

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

async function loadGames() {
  allGames.value = await fetchGameStatsList(props.years, props.playerCounts);
}

async function loadPopular() {
  loadingPopular.value = true;
  try {
    popular.value = await fetchPopularGames(props.years, props.playerCounts);
  } finally {
    loadingPopular.value = false;
  }
}

// Selecting a picked/banned game opens its full leaderboard, same as tapping
// it in the game picker below.
function onSelectPopularGame(gameId: number) {
  selectedGameId.value = gameId;
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
      props.years,
      props.playerCounts
    );
  } finally {
    loadingLeaderboard.value = false;
  }
}

watch(
  () => [props.years, props.playerCounts],
  () => {
    void loadGames();
    void loadPopular();
    void loadLeaderboard();
  },
  { deep: true }
);

watch(selectedGameId, () => {
  void loadLeaderboard();
});

onMounted(() => {
  void loadGames();
  void loadPopular();
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

// Section header that labels the "Games" side of the split stats layout.
.section-header {
  gap: 10px;

  &__icon {
    width: 38px;
    height: 38px;
    border-radius: 9px;
    background: rgba(99, 102, 241, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
}

.game-preview-list {
  max-height: 320px;
  overflow-y: auto;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  transition: max-height 0.2s ease;

  // Fewer rows in view at once on phones -- easier to scan, with the
  // scrollbar making it obvious there's more below.
  @media (max-width: 599px) {
    max-height: 200px;
  }

  // Once a game is picked, the picker itself is no longer the focus --
  // shrink it so the leaderboard below gets the room instead.
  &--collapsed {
    max-height: 120px;
  }
}

.selected-game-header {
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
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

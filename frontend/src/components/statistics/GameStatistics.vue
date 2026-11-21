<template>
  <div class="game-statistics">
    <!-- Picks & Bans Section -->
    <div class="q-mb-xl">
      <div class="section-header row items-center no-wrap q-mb-md">
        <div class="section-header__icon">
          <q-icon name="leaderboard" color="primary" size="20px" />
        </div>
        <div class="column">
          <div class="text-h6 text-weight-bolder text-dark line-height-1">
            Picks &amp; Bans
          </div>
          <div class="text-caption text-grey-6">
            The games players choose most &mdash; and veto most across seasons.
          </div>
        </div>
      </div>

      <q-skeleton
        v-if="loadingPopular"
        type="rect"
        height="180px"
        class="rounded-borders"
      />
      <PopularGamesCard
        v-else
        :popular="popular"
        @select="onSelectPopularGame"
      />
    </div>

    <!-- Game Masteries & Leaderboard Explorer Section -->
    <div>
      <div class="section-header row items-center no-wrap q-mb-md">
        <div class="section-header__icon">
          <q-icon name="sports_esports" color="primary" size="20px" />
        </div>
        <div class="column">
          <div class="text-h6 text-weight-bolder text-dark line-height-1">
            Game Leaderboards
          </div>
          <div class="text-caption text-grey-6">
            Search any game to see who masters it and view full player rankings.
          </div>
        </div>
      </div>

      <div class="row q-col-gutter-lg">
        <!-- Game List Column -->
        <div class="col-12 col-md-5 col-lg-4">
          <q-card flat bordered class="game-selector-card">
            <q-card-section class="q-pb-xs">
              <q-input
                v-model="gameSearch"
                label="Search games"
                clearable
                dense
                outlined
                class="q-mb-sm"
              >
                <template v-slot:prepend>
                  <q-icon name="search" />
                </template>
              </q-input>
            </q-card-section>

            <q-separator class="q-mx-md q-mb-sm" />

            <q-card-section class="q-pt-none">
              <div class="game-preview-list">
                <div
                  v-for="game in filteredGames"
                  :key="game.game_id"
                  class="game-preview-row row items-center justify-between no-wrap"
                  :class="{
                    'game-preview-row--active': game.game_id === selectedGameId,
                  }"
                  @click="
                    selectedGameId =
                      selectedGameId === game.game_id ? null : game.game_id
                  "
                >
                  <div class="game-preview-row__name ellipsis text-weight-bold">
                    {{ game.name }}
                  </div>
                  <div
                    v-if="game.best_player"
                    class="game-preview-row__best text-caption ellipsis"
                  >
                    <q-icon
                      name="emoji_events"
                      size="14px"
                      class="text-amber-8 q-mr-xs"
                    />
                    {{ game.best_player.profile_name }}
                    <span
                      v-if="game.best_player.win_rate !== null"
                      class="text-grey-6"
                    >
                      &middot; {{ game.best_player.win_rate }}%
                    </span>
                  </div>
                  <div v-else class="text-caption text-grey-5">
                    No ranked player
                  </div>
                </div>
                <div
                  v-if="filteredGames.length === 0"
                  class="text-caption text-grey-6 q-pa-sm"
                >
                  No games match that search.
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Desktop / Tablet Leaderboard Column -->
        <div v-if="!smallScreen" class="col-12 col-md-7 col-lg-8">
          <q-card
            v-if="selectedGameId !== null"
            flat
            bordered
            class="game-details-card"
          >
            <q-card-section class="q-pb-sm">
              <div class="row items-center justify-between no-wrap">
                <div class="row items-center no-wrap">
                  <div class="stat-icon-box q-mr-sm">
                    <q-icon name="emoji_events" color="primary" size="22px" />
                  </div>
                  <div class="column">
                    <div
                      class="text-h6 text-weight-bolder text-dark line-height-1"
                    >
                      {{ selectedGame?.name }}
                    </div>
                    <div class="text-caption text-grey-6 q-mt-xs">
                      {{ selectedGame?.platform || 'Board Game' }} &middot;
                      {{ selectedGame?.games_played ?? 0 }} games played
                    </div>
                  </div>
                </div>

                <KennerButton
                  flat
                  round
                  dense
                  size="sm"
                  icon="close"
                  color="grey-7"
                  @click="selectedGameId = null"
                />
              </div>
            </q-card-section>

            <q-separator class="q-mx-md" />

            <q-card-section>
              <GameLeaderboardPanel
                :loading="loadingLeaderboard"
                :leaderboard="leaderboard"
                :fame-leaders="fameLeaders"
                :columns="gameLeaderboardColumns"
              />
            </q-card-section>
          </q-card>

          <!-- Empty Selection Placeholder -->
          <q-card
            v-else
            flat
            bordered
            class="empty-selection-card flex flex-center q-pa-xl"
          >
            <div class="column items-center text-center">
              <div class="empty-icon-box q-mb-md">
                <q-icon name="sports_esports" size="36px" color="primary" />
              </div>
              <div
                class="text-subtitle1 text-weight-bolder text-dark q-mb-xs"
              >
                Select a Game
              </div>
              <div
                class="text-caption text-grey-6"
                style="max-width: 320px"
              >
                Choose a game from the list on the left to see its expert players,
                win rates, and full player rankings.
              </div>
            </div>
          </q-card>
        </div>
      </div>
    </div>

    <!-- Mobile dialog for leaderboard -->
    <q-dialog
      v-model="mobileLeaderboardOpen"
      maximized
      transition-show="slide-up"
      transition-hide="slide-down"
    >
      <q-card class="mobile-leaderboard-card">
        <div class="mobile-leaderboard-header row items-center no-wrap">
          <q-icon
            name="emoji_events"
            size="22px"
            color="white"
            class="q-mr-sm"
          />
          <div class="text-subtitle1 text-weight-bolder text-white ellipsis">
            {{ selectedGame?.name ?? 'Leaderboard' }}
          </div>
          <q-space />
          <KennerButton
            flat
            round
            dense
            icon="close"
            color="white"
            aria-label="Close"
            v-close-popup
          />
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
import KennerButton from 'components/base/KennerButton.vue';
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

const { smallScreen } = useResponsive();

const popular = ref<TPopularGames | null>(null);
const loadingPopular = ref(false);

const allGames = ref<TGameStatSummary[]>([]);
const gameSearch = ref('');
const filteredGames = computed(() => {
  const needle = gameSearch.value.trim().toLowerCase();
  if (!needle) return allGames.value;
  return allGames.value.filter((game) =>
    game.name.toLowerCase().includes(needle)
  );
});

const selectedGameId = ref<number | null>(null);
const selectedGame = computed(
  () =>
    allGames.value.find((game) => game.game_id === selectedGameId.value) ?? null
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

.empty-icon-box {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: rgba(99, 102, 241, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-selection-card {
  min-height: 360px;
}

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
  max-height: 420px;
  overflow-y: auto;
  border: 1px solid var(--kenner-border-color);
  border-radius: 8px;

  @media (max-width: 599px) {
    max-height: 240px;
  }
}

.game-preview-row {
  padding: 8px 12px;
  cursor: pointer;
  gap: 12px;
  border-bottom: 1px solid var(--kenner-border-subtle);
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

.mobile-leaderboard-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  border-radius: 0 !important;
}

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

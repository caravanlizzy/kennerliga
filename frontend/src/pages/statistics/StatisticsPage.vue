<template>
  <q-page class="q-pa-md max-width-container q-mx-auto statistics-page">
    <div class="row items-center justify-between q-mb-md q-col-gutter-y-sm">
      <div class="row items-center q-gutter-x-sm">
        <div class="stat-icon-box stat-icon-box--lg">
          <q-icon name="query_stats" color="primary" size="24px" />
        </div>
        <div class="text-body2 text-grey-7">Rankings, records &amp; leaderboards.</div>
      </div>

      <div class="row items-center q-gutter-x-md">
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

        <div style="min-width: 180px">
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

        <div v-if="loadingLeaderboard" class="flex justify-center q-pa-lg">
          <q-spinner color="primary" size="32px" />
        </div>

        <template v-else-if="leaderboard">
          <div class="text-caption text-grey-6 q-mb-sm">
            {{ leaderboard.platform }}
          </div>

          <!-- Hall of Fame: the three most dominant players at this game,
               ranked by win % divided by average position (a higher win
               rate combined with a lower/better average position wins). -->
          <div v-if="fameLeaders.length > 0" class="fame-card q-mb-md">
            <div class="fame-card__header row items-center no-wrap q-mb-sm">
              <q-icon name="emoji_events" size="18px" color="primary" class="q-mr-xs" />
              <span class="text-weight-bolder text-dark">Hall of Fame</span>
              <q-space />
              <span class="text-caption text-grey-6">Win % ÷ Avg Pos</span>
            </div>
            <div class="row q-col-gutter-sm">
              <div
                v-for="(leader, idx) in fameLeaders"
                :key="leader.profile_id"
                class="col"
              >
                <div class="fame-player">
                  <span class="rank-badge">{{ idx + 1 }}</span>
                  <div
                    class="fame-player__name ellipsis"
                    :class="{ 'text-weight-bolder text-primary': leader.is_me }"
                  >
                    {{ leader.profile_name }}
                  </div>
                  <div class="fame-player__score text-weight-bolder text-dark">
                    {{ leader.fameScore.toFixed(2) }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div
            v-if="!leaderboard.me.eligible"
            class="me-row row items-center justify-between q-pa-sm q-mb-sm rounded-borders me-row--unranked"
          >
            <span class="text-weight-bold">You</span>
            <span class="text-caption text-grey-6">
              {{ leaderboard.me.games_played }} game(s) played &middot; no ranking yet
            </span>
          </div>

          <KennerTable
            v-if="leaderboard.leaderboard.length > 0"
            flat
            :rows="leaderboard.leaderboard"
            :columns="gameLeaderboardColumns"
            row-key="profile_id"
          >
            <template v-slot:body-cell-profile_name="props">
              <q-td :props="props">
                <span :class="{ 'text-weight-bolder text-primary': props.row.is_me }">
                  {{ props.row.profile_name }}
                  <q-badge
                    v-if="props.row.is_me"
                    color="primary"
                    text-color="white"
                    class="q-ml-xs"
                    label="you"
                  />
                </span>
              </q-td>
            </template>
          </KennerTable>
          <div v-else class="text-caption text-grey-6 q-pa-md">
            No one has played this game yet.
          </div>
        </template>

        <div v-else-if="selectedGameId === null" class="text-caption text-grey-6 q-pa-md">
          Pick a game above to see its full leaderboard.
        </div>
      </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
defineOptions({ name: 'StatisticsPage' });

import { computed, onMounted, ref, watch } from 'vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import KennerTable from 'components/tables/KennerTable.vue';
import StatCategoryCard from 'components/statistics/StatCategoryCard.vue';
import { useUserStore } from 'stores/userStore';
import {
  fetchGameLeaderboard,
  fetchGameStatsList,
  fetchStatisticsOverview,
} from 'src/services/statisticsService';
import { TGameLeaderboard, TGameStatSummary, TStatisticsOverview } from 'src/types';

const { getAvailableYears } = useUserStore();

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
const leaderboard = ref<TGameLeaderboard | null>(null);
const loadingLeaderboard = ref(false);

// The three most dominant players at the selected game: win rate divided by
// average position, so a high win % paired with a low (better) average
// position rises to the top. Only ranked players with both metrics qualify.
const fameLeaders = computed(() => {
  if (!leaderboard.value) return [];
  return leaderboard.value.leaderboard
    .filter(
      (entry) =>
        entry.eligible &&
        entry.win_rate !== null &&
        entry.avg_position !== null &&
        entry.avg_position > 0
    )
    .map((entry) => ({
      ...entry,
      fameScore: (entry.win_rate as number) / (entry.avg_position as number),
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

.me-row {
  background: rgba(99, 102, 241, 0.06);
  border: 1px solid rgba(99, 102, 241, 0.15);
}

.me-row--unranked {
  background: rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.game-preview-list {
  max-height: 320px;
  overflow-y: auto;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 8px;
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

// Hall of Fame: a plain bordered panel matching the app's flat card style
// (no gradients).
.fame-card {
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
}

.fame-player {
  height: 100%;
  text-align: center;
  padding: 10px 6px 8px;
  border-radius: 8px;
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: border-color 0.15s ease;

  &:hover {
    border-color: rgba(99, 102, 241, 0.25);
  }

  &__name {
    font-size: 12px;
    line-height: 1.2;
    margin-top: 6px;
  }

  &__score {
    font-size: 15px;
    margin-top: 2px;
  }
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.06);
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
}

// Keep the per-game panel visible while scrolling the (usually taller)
// column of category cards next to it on wide screens.
@media (min-width: 1024px) {
  .game-stats-card {
    position: sticky;
    top: 16px;
  }
}
</style>

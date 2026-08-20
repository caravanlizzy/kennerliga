<template>
  <q-page class="q-pa-md max-width-container q-mx-auto statistics-page">
    <div class="row items-center justify-between q-mb-md">
      <div class="row items-center q-gutter-x-sm">
        <q-icon name="query_stats" size="sm" color="primary" />
        <div class="text-h6 text-weight-bolder">Statistics</div>
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

    <!-- Player-count filter, mirroring the chips on the players list. -->
    <div class="row items-center q-gutter-x-sm q-mb-md">
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

    <!-- Split layout: ranking categories on the left, the per-game
         leaderboard pinned top-right so it is visible without scrolling
         past all the category cards first. -->
    <div class="row q-col-gutter-md">
      <div class="col-12 col-md-7 order-last order-md-first">
        <div v-if="loadingOverview" class="row q-col-gutter-md">
          <div v-for="i in 4" :key="i" class="col-12 col-sm-6">
            <q-skeleton type="rect" height="240px" class="rounded-borders" />
          </div>
        </div>

        <div v-else class="row q-col-gutter-md">
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
      <q-card-section class="q-pb-none">
        <div class="row items-center no-wrap">
          <div class="stat-icon-box q-mr-sm">
            <q-icon name="sports_esports" color="primary" size="22px" />
          </div>
          <div class="column">
            <div class="text-subtitle1 text-weight-bolder text-dark">Best Players by Game</div>
            <div class="text-caption text-grey-6">Pick a game to see who performs best at it.</div>
          </div>
        </div>
      </q-card-section>

      <q-card-section>
        <q-select
          v-model="selectedGameId"
          :options="gameOptions"
          label="Select a game"
          clearable
          dense
          outlined
          emit-value
          map-options
          class="q-mb-md game-select"
        >
          <template v-slot:option="scope">
            <q-item v-bind="scope.itemProps">
              <q-item-section>
                <q-item-label>{{ scope.opt.label }}</q-item-label>
                <q-item-label caption>
                  {{ scope.opt.games_played }} games played &middot; {{ scope.opt.distinct_players }} players
                </q-item-label>
              </q-item-section>
            </q-item>
          </template>
        </q-select>

        <div v-if="loadingLeaderboard" class="flex justify-center q-pa-lg">
          <q-spinner color="primary" size="32px" />
        </div>

        <template v-else-if="leaderboard">
          <div class="text-caption text-grey-6 q-mb-sm">
            {{ leaderboard.platform }} &middot; min {{ leaderboard.min_games }} games played to be ranked
            <span v-if="leaderboard.excluded_low_sample_count > 0">
              ({{ leaderboard.excluded_low_sample_count }} player(s) below that threshold are hidden)
            </span>
          </div>

          <!-- Hall of Fame: the three most dominant players at this game,
               ranked by win % divided by average position (a higher win
               rate combined with a lower/better average position wins). -->
          <div v-if="fameLeaders.length > 0" class="fame-card q-mb-md">
            <div class="fame-card__header row items-center no-wrap">
              <q-icon name="emoji_events" size="18px" class="q-mr-xs" />
              <span class="text-weight-bolder">Hall of Fame</span>
              <q-space />
              <span class="fame-card__subtitle">Win % ÷ Avg Pos</span>
            </div>
            <div class="row q-col-gutter-sm q-mt-sm">
              <div
                v-for="(leader, idx) in fameLeaders"
                :key="leader.profile_id"
                class="col"
              >
                <div class="fame-player" :class="`fame-player--${idx + 1}`">
                  <q-icon
                    :name="idx === 0 ? 'emoji_events' : 'military_tech'"
                    size="22px"
                    class="fame-player__medal"
                  />
                  <div
                    class="fame-player__name ellipsis"
                    :class="{ 'text-weight-bolder': leader.is_me }"
                  >
                    {{ leader.profile_name }}
                  </div>
                  <div class="fame-player__score">{{ leader.fameScore.toFixed(2) }}</div>
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
              {{ leaderboard.me.games_played }} game(s) played &middot; need {{ leaderboard.min_games }}+ to be ranked
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
            No player has reached the {{ leaderboard.min_games }}-game minimum for this game yet.
          </div>
        </template>

        <div v-else-if="selectedGameId === null" class="text-caption text-grey-6 q-pa-md">
          Search for a game above to see its leaderboard.
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
const gameOptions = computed(() =>
  allGames.value.map((game) => ({
    label: game.name,
    value: game.game_id,
    games_played: game.games_played,
    distinct_players: game.distinct_players,
  }))
);
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

.me-row {
  background: rgba(99, 102, 241, 0.06);
  border: 1px solid rgba(99, 102, 241, 0.15);
}

.me-row--unranked {
  background: rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.game-select {
  max-width: 420px;
}

// Hall of Fame flair: a warm golden gradient panel that lifts the top
// three players above the plain leaderboard table.
.fame-card {
  border-radius: 12px;
  padding: 12px 14px;
  background: linear-gradient(135deg, #fff8e1 0%, #ffe7ba 100%);
  border: 1px solid rgba(217, 164, 6, 0.35);
  box-shadow: 0 2px 10px rgba(217, 164, 6, 0.18);

  &__header {
    color: #8a6d02;
  }

  &__subtitle {
    font-size: 11px;
    color: #a9862b;
  }
}

.fame-player {
  position: relative;
  height: 100%;
  text-align: center;
  padding: 10px 6px 8px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(217, 164, 6, 0.25);

  &__medal {
    color: #b8860b;
  }

  &__name {
    font-size: 12px;
    line-height: 1.2;
    margin-top: 2px;
    color: #5f4b06;
  }

  &__score {
    font-weight: 800;
    font-size: 15px;
    color: #7a5c00;
  }

  &--1 {
    background: linear-gradient(160deg, #fff3c4 0%, #ffd54f 100%);
    border-color: rgba(217, 164, 6, 0.6);
    box-shadow: 0 2px 8px rgba(217, 164, 6, 0.3);

    .fame-player__medal {
      color: #d4a006;
    }
  }

  &--2 .fame-player__medal {
    color: #9e9e9e;
  }

  &--3 .fame-player__medal {
    color: #b07b46;
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
</style>

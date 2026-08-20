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

    <div v-if="loadingOverview" class="row q-col-gutter-md q-mb-lg">
      <div v-for="i in 6" :key="i" class="col-12 col-sm-6 col-md-4">
        <q-skeleton type="rect" height="240px" class="rounded-borders" />
      </div>
    </div>

    <div v-else class="row q-col-gutter-md q-mb-lg">
      <div
        v-for="category in overview?.categories ?? []"
        :key="category.key"
        class="col-12 col-sm-6 col-md-4"
      >
        <StatCategoryCard :category="category" />
      </div>
    </div>

    <q-card flat bordered>
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
          :options="filteredGameOptions"
          label="Search a game..."
          use-input
          clearable
          dense
          outlined
          emit-value
          map-options
          input-debounce="150"
          class="q-mb-md game-select"
          @filter="filterGames"
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
const filteredGameOptions = ref<typeof gameOptions.value>([]);

function filterGames(val: string, update: (callback: () => void) => void) {
  update(() => {
    if (!val) {
      filteredGameOptions.value = gameOptions.value;
      return;
    }
    const needle = val.toLowerCase();
    filteredGameOptions.value = gameOptions.value.filter((option) =>
      option.label.toLowerCase().includes(needle)
    );
  });
}

const selectedGameId = ref<number | null>(null);
const leaderboard = ref<TGameLeaderboard | null>(null);
const loadingLeaderboard = ref(false);

async function loadOverview() {
  loadingOverview.value = true;
  try {
    overview.value = await fetchStatisticsOverview({ years: selectedYears.value });
  } finally {
    loadingOverview.value = false;
  }
}

async function loadGames() {
  allGames.value = await fetchGameStatsList(selectedYears.value);
  filteredGameOptions.value = gameOptions.value;
}

async function loadLeaderboard() {
  if (selectedGameId.value === null) {
    leaderboard.value = null;
    return;
  }
  loadingLeaderboard.value = true;
  try {
    leaderboard.value = await fetchGameLeaderboard(selectedGameId.value, selectedYears.value);
  } finally {
    loadingLeaderboard.value = false;
  }
}

watch(
  selectedYears,
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
    name: 'wins',
    label: 'Wins',
    align: 'right',
    field: (row: { wins: number }) => row.wins,
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
  {
    name: 'podiums',
    label: 'Podiums',
    align: 'right',
    field: (row: { podiums: number }) => row.podiums,
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
</style>

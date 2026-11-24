<template>
  <div class="games-list-page">
    <!-- Header & Filter Toolbar -->
    <div
      class="filter-toolbar row items-center justify-between"
      :class="isMobile ? 'q-mb-sm' : 'q-mb-md'"
    >
      <div
        class="filter-controls row items-center"
        :class="isMobile ? 'q-col-gutter-xs' : 'q-col-gutter-md'"
      >
        <!-- Player Count Filter -->
        <div class="filter-item row items-center">
          <KennerPlayerCountFilter
            v-model="selectedPlayerCounts"
            :available-counts="availablePlayerCounts"
            label="Players:"
          />
        </div>

        <!-- Years Multi-select Filter -->
        <div class="filter-item row items-center q-gutter-x-xs">
          <div
            class="row items-center text-caption text-weight-bold text-grey-8 filter-label"
          >
            <q-icon
              name="calendar_today"
              :size="isMobile ? '14px' : '16px'"
              class="q-mr-xs text-primary"
            />
            <span v-if="!isMobile">Years:</span>
          </div>
          <q-select
            v-model="selectedYears"
            :options="availableYears"
            multiple
            clearable
            dense
            outlined
            options-dense
            placeholder="All Years"
            :display-value="
              !selectedYears || selectedYears.length === 0
                ? 'All Years'
                : selectedYears
                    .slice()
                    .sort((a, b) => b - a)
                    .join(', ')
            "
            class="bg-white rounded-borders years-select"
            :class="isMobile ? 'years-select--mobile' : ''"
          >
            <template v-slot:prepend>
              <q-icon name="event" size="xs" color="grey-6" />
            </template>
          </q-select>
        </div>
      </div>

      <!-- Right actions: View mode toggle & Admin Create button -->
      <div class="row items-center q-gutter-xs">
        <q-btn-toggle
          v-model="viewMode"
          dense
          flat
          rounded
          toggle-color="primary"
          color="grey-7"
          :options="[
            { icon: 'grid_view', value: 'grid' },
            { icon: 'view_list', value: 'table' },
          ]"
        >
          <q-tooltip>Toggle View Mode</q-tooltip>
        </q-btn-toggle>

        <KennerButton
          v-if="isAdmin"
          color="secondary"
          label="Game"
          icon="add_circle"
          size="sm"
          :to="{ name: 'game-create' }"
        />
      </div>
    </div>

    <!-- Error Banner -->
    <q-banner v-if="error" rounded dense class="q-mb-md bg-negative text-white">
      <template #avatar><q-icon name="warning" color="white" /></template>
      {{ error }}
    </q-banner>

    <!-- Picks & Bans Showcase -->
    <div :class="isMobile ? 'q-mb-md' : 'q-mb-lg'">
      <q-skeleton
        v-if="loadingPopular"
        type="rect"
        height="140px"
        class="rounded-borders"
      />
      <PopularGamesCard v-else :popular="popular" @select="navigateToGame" />
    </div>

    <!-- Grid View Mode -->
    <div v-if="viewMode === 'grid'">
      <q-card flat bordered class="games-grid-card">
        <q-card-section class="q-pb-xs">
          <div class="row items-center justify-between q-col-gutter-sm">
            <div class="col-12 col-sm-6 col-md-4">
              <q-input
                v-model="gameSearch"
                label="Search games"
                clearable
                dense
                outlined
              >
                <template v-slot:prepend>
                  <q-icon name="search" />
                </template>
              </q-input>
            </div>
            <div class="col-12 col-sm-auto text-caption text-grey-6">
              Showing {{ filteredGames.length }} games
            </div>
          </div>
        </q-card-section>

        <q-separator class="q-mx-md q-my-sm" />

        <q-card-section class="q-pt-none">
          <div v-if="loadingGames" class="row q-col-gutter-md">
            <div
              v-for="i in 6"
              :key="`sk-g-${i}`"
              class="col-12 col-sm-6 col-md-4 col-lg-3"
            >
              <q-skeleton type="rect" height="150px" class="rounded-borders" />
            </div>
          </div>

          <div
            v-else
            class="row"
            :class="isMobile ? 'q-col-gutter-sm' : 'q-col-gutter-md'"
          >
            <div
              v-for="game in filteredGames"
              :key="game.id"
              class="col-12 col-sm-6 col-md-4 col-lg-3"
            >
              <div
                class="game-card-link q-pa-md rounded-borders column justify-between"
                @click="navigateToGame(game.id)"
              >
                <div>
                  <div class="row items-center justify-between no-wrap q-mb-xs">
                    <q-badge
                      color="grey-3"
                      text-color="grey-8"
                      class="text-weight-bold"
                    >
                      {{ game.platformName || 'Board Game' }}
                    </q-badge>
                    <div class="row items-center no-wrap q-gutter-x-xs">
                      <span class="text-caption text-grey-6 text-weight-medium">
                        {{ game.games_played }} plays
                      </span>
                      <template v-if="isAdmin">
                        <q-btn
                          flat
                          round
                          dense
                          size="xs"
                          icon="settings"
                          color="secondary"
                          @click.stop="
                            router.push({
                              name: 'game-config',
                              params: { id: game.id },
                            })
                          "
                        >
                          <q-tooltip>Configure Game</q-tooltip>
                        </q-btn>
                        <q-btn
                          flat
                          round
                          dense
                          size="xs"
                          icon="edit"
                          color="grey-7"
                          @click.stop="
                            router.push({
                              name: 'game-edit',
                              params: { id: game.id },
                            })
                          "
                        >
                          <q-tooltip>Edit Game</q-tooltip>
                        </q-btn>
                      </template>
                    </div>
                  </div>

                  <div
                    class="text-subtitle1 text-weight-bolder text-grey-9 ellipsis-2-lines q-mb-sm"
                  >
                    {{ game.name }}
                  </div>
                </div>

                <div
                  class="border-top-subtle q-pt-sm row items-center justify-between no-wrap"
                >
                  <div
                    v-if="game.best_player"
                    class="text-caption ellipsis text-grey-8"
                  >
                    <q-icon
                      name="emoji_events"
                      size="14px"
                      class="text-amber-8 q-mr-xs"
                    />
                    <span class="text-weight-bold">{{
                      game.best_player.profile_name
                    }}</span>
                    <span
                      v-if="game.best_player.win_rate !== null"
                      class="text-grey-6"
                    >
                      ({{ game.best_player.win_rate }}%)
                    </span>
                  </div>
                  <div v-else class="text-caption text-grey-5">
                    No ranked plays
                  </div>

                  <q-icon name="chevron_right" color="primary" size="20px" />
                </div>
              </div>
            </div>

            <div
              v-if="filteredGames.length === 0"
              class="col-12 text-center q-py-xl text-grey-6"
            >
              <q-icon
                name="search_off"
                size="36px"
                class="q-mb-sm text-grey-4"
              />
              <div>No games match "{{ gameSearch }}".</div>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Table View Mode -->
    <div v-else>
      <KennerTable
        flat
        row-key="id"
        @row-click="onRowClick"
        :rows="filteredGames"
        :columns="tableColumns"
        :loading="loadingGames"
      >
        <template v-slot:body-cell-actions="props">
          <q-td :props="props" class="q-gutter-x-xs">
            <q-btn
              flat
              round
              dense
              size="sm"
              icon="query_stats"
              color="primary"
              title="View Statistics"
              @click.stop="navigateToGame(props.row.id)"
            />
            <q-btn
              v-if="isAdmin"
              flat
              round
              dense
              size="sm"
              icon="settings"
              color="secondary"
              title="View Configuration"
              @click.stop="
                router.push({
                  name: 'game-config',
                  params: { id: props.row.id },
                })
              "
            />
            <q-btn
              v-if="isAdmin"
              flat
              round
              dense
              size="sm"
              icon="edit"
              color="grey-7"
              title="Edit Game"
              @click.stop="
                router.push({
                  name: 'game-edit',
                  params: { id: props.row.id },
                })
              "
            />
          </q-td>
        </template>
      </KennerTable>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useUserStore } from 'stores/userStore';
import { useResponsive } from 'src/composables/responsive';
import KennerTable from 'components/tables/KennerTable.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerPlayerCountFilter from 'components/base/KennerPlayerCountFilter.vue';
import PopularGamesCard from 'components/statistics/PopularGamesCard.vue';
import {
  fetchGamesForManagement,
  fetchPlatforms,
} from 'src/services/gameService';
import {
  fetchGameStatsList,
  fetchPopularGames,
} from 'src/services/statisticsService';
import {
  TGameDto,
  TGameStatSummary,
  TPlatform,
  TPopularGames,
} from 'src/types';

const router = useRouter();
const { isMobile } = useResponsive();
const userStore = useUserStore();
const { isAdmin } = storeToRefs(userStore);

const availablePlayerCounts = ['2p', '3p', '4p'];
const selectedPlayerCounts = ref<string[]>([]);
const selectedYears = ref<number[]>([]);
const availableYears = ref<number[]>([]);

const playerCountsParam = computed<string[] | undefined>(() => {
  if (selectedPlayerCounts.value.length === 0) return undefined;
  return selectedPlayerCounts.value;
});

const viewMode = ref<'grid' | 'table'>('grid');
const gameSearch = ref('');

const allGames = ref<TGameDto[]>([]);
const platforms = ref<TPlatform[]>([]);
const statSummaries = ref<TGameStatSummary[]>([]);
const popular = ref<TPopularGames | null>(null);

const loadingGames = ref(false);
const loadingPopular = ref(false);
const error = ref<string | null>(null);

const platformMap = computed<Record<string, string>>(() => {
  const map: Record<string, string> = {};
  for (const p of platforms.value) {
    map[String(p.id)] = p.name;
  }
  return map;
});

function lookupPlatform(game: TGameDto) {
  return platformMap.value[String(game.platform)] ?? 'Board Game';
}

interface EnrichedGame extends TGameDto {
  platformName: string;
  games_played: number;
  distinct_players: number;
  best_player: {
    profile_id: number;
    profile_name: string;
    win_rate: number | null;
    avg_position: number | null;
  } | null;
}

const enrichedGames = computed<EnrichedGame[]>(() => {
  const statsMap = new Map<number, TGameStatSummary>();
  for (const s of statSummaries.value) {
    statsMap.set(s.game_id, s);
  }
  return allGames.value.map((game) => {
    const stat = statsMap.get(game.id);
    return {
      ...game,
      platformName: lookupPlatform(game),
      games_played: stat?.games_played ?? 0,
      distinct_players: stat?.distinct_players ?? 0,
      best_player: stat?.best_player ?? null,
    };
  });
});

const filteredGames = computed(() => {
  const needle = gameSearch.value.trim().toLowerCase();
  if (!needle) return enrichedGames.value;
  return enrichedGames.value.filter(
    (g) =>
      g.name.toLowerCase().includes(needle) ||
      g.platformName.toLowerCase().includes(needle)
  );
});

async function loadData() {
  loadingGames.value = true;
  loadingPopular.value = true;
  error.value = null;

  try {
    const [gamesData, platformsData, statsData, popularData] =
      await Promise.all([
        fetchGamesForManagement(),
        fetchPlatforms(),
        fetchGameStatsList(selectedYears.value, playerCountsParam.value),
        fetchPopularGames(selectedYears.value, playerCountsParam.value),
      ]);
    allGames.value = gamesData;
    platforms.value = platformsData;
    statSummaries.value = statsData;
    popular.value = popularData;
  } catch (err: unknown) {
    error.value =
      err instanceof Error ? err.message : 'Failed to load games list';
  } finally {
    loadingGames.value = false;
    loadingPopular.value = false;
  }
}

function navigateToGame(gameId: number) {
  void router.push({ name: 'game-detail', params: { id: gameId } });
}

function onRowClick(_evt: unknown, row: EnrichedGame) {
  navigateToGame(row.id);
}

const tableColumns = computed(() => [
  {
    name: 'game',
    label: 'Game',
    field: (x: EnrichedGame) => x.name,
    align: 'left' as const,
    sortable: true,
  },
  {
    name: 'platform',
    label: 'Platform',
    field: (x: EnrichedGame) => x.platformName,
    align: 'left' as const,
    sortable: true,
  },
  {
    name: 'plays',
    label: 'Plays',
    field: (x: EnrichedGame) => x.games_played,
    align: 'right' as const,
    sortable: true,
  },
  {
    name: 'actions',
    label: 'Actions',
    field: () => '',
    align: 'right' as const,
    sortable: false,
  },
]);

watch(
  () => [selectedYears.value, selectedPlayerCounts.value],
  () => {
    void loadData();
  },
  { deep: true }
);

onMounted(async () => {
  availableYears.value = await userStore.getAvailableYears();
  await loadData();
});
</script>

<style scoped lang="scss">
.games-list-page {
  width: 100%;
}

.years-select {
  min-width: 160px;
  max-width: 280px;

  &--mobile {
    min-width: 130px;
    max-width: 180px;
  }
}

.filter-label {
  white-space: nowrap;
}

.games-grid-card {
  border-radius: 12px;
}

.game-card-link {
  min-height: 120px;
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid var(--kenner-border-subtle);
  cursor: pointer;
  transition: all 0.2s ease;

  .body--dark & {
    background: rgba(255, 255, 255, 0.02);
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
    border-color: var(--q-primary);
  }
}

.border-top-subtle {
  border-top: 1px solid var(--kenner-border-subtle);
}
</style>

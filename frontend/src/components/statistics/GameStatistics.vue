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
      <PopularGamesCard v-else :popular="popular" @select="navigateToGame" />
    </div>

    <!-- Games Directory & Leaderboards Explorer -->
    <div>
      <div class="section-header row items-center no-wrap q-mb-md">
        <div class="section-header__icon">
          <q-icon name="sports_esports" color="primary" size="20px" />
        </div>
        <div class="column">
          <div class="text-h6 text-weight-bolder text-dark line-height-1">
            Game Directory &amp; Stats
          </div>
          <div class="text-caption text-grey-6">
            Click any game to open its dedicated page with high scores,
            masteries, full player rankings, and match history.
          </div>
        </div>
      </div>

      <q-card flat bordered class="game-selector-card">
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
          <div class="row q-col-gutter-md">
            <div
              v-for="game in filteredGames"
              :key="game.game_id"
              class="col-12 col-sm-6 col-md-4 col-lg-3"
            >
              <div
                class="game-card-link q-pa-md rounded-borders column justify-between"
                @click="navigateToGame(game.game_id)"
              >
                <div>
                  <div class="row items-center justify-between no-wrap q-mb-xs">
                    <q-badge
                      color="grey-3"
                      text-color="grey-8"
                      class="text-weight-bold"
                    >
                      {{ game.platform || 'Board Game' }}
                    </q-badge>
                    <span class="text-caption text-grey-6 text-weight-medium">
                      {{ game.games_played }} plays
                    </span>
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
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'GameStatistics' });

import { computed, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import PopularGamesCard from 'components/statistics/PopularGamesCard.vue';
import {
  fetchGameStatsList,
  fetchPopularGames,
} from 'src/services/statisticsService';
import { TGameStatSummary, TPopularGames } from 'src/types';

const props = defineProps<{
  years: number[];
  playerCounts: string[] | undefined;
}>();

const router = useRouter();

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

function navigateToGame(gameId: number) {
  router.push({
    name: 'game-detail',
    params: { id: gameId },
  });
}

watch(
  () => [props.years, props.playerCounts],
  () => {
    void loadPopular();
    void loadGames();
  },
  { deep: true }
);

onMounted(() => {
  void loadPopular();
  void loadGames();
});
</script>

<style scoped lang="scss">
.section-header {
  &__icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: rgba(99, 102, 241, 0.08);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 12px;
    flex-shrink: 0;
  }
}

.game-selector-card {
  border-radius: 12px;
  background: var(--kenner-surface-overlay, #ffffff);
  border: 1px solid var(--kenner-border-color, rgba(0, 0, 0, 0.08));
}

.game-card-link {
  min-height: 110px;
  background: var(--kenner-bg-glass-card, #ffffff);
  border: 1px solid var(--kenner-border-color, rgba(0, 0, 0, 0.08));
  cursor: pointer;
  transition: transform 0.15s ease, border-color 0.15s ease,
    box-shadow 0.15s ease;

  &:hover {
    transform: translateY(-2px);
    border-color: var(--kenner-primary, #6366f1);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
  }
}

.border-top-subtle {
  border-top: 1px solid var(--kenner-border-subtle, rgba(0, 0, 0, 0.05));
}
</style>

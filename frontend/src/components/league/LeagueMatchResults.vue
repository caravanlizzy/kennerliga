<template>
  <div class="league-match-results">
    <div v-if="loading" class="flex justify-center q-pa-lg">
      <LoadingSpinner text="Loading match results..." />
    </div>

    <div v-else-if="selectedGamesWithResults.length === 0" class="column items-center q-pa-xl text-grey-6 bg-white rounded-borders border-subtle">
      <q-icon name="history" size="48px" class="q-mb-md opacity-20" />
      <div class="text-subtitle1">No match results yet</div>
      <div class="text-caption">The results will appear here once games are played and recorded.</div>
    </div>

    <div v-else class="row q-col-gutter-md items-start">
      <!-- Standings card: smaller, own column, kept visually distinct from the results -->
      <div v-if="showStandings" class="col-12 col-md-4 col-lg-3">
        <q-card flat class="match-game-card standings-card">
          <q-card-section class="q-pb-none">
            <div class="row items-center no-wrap">
              <div class="game-icon-box q-mr-sm">
                <q-icon name="leaderboard" color="primary" size="24px" />
              </div>
              <div class="column">
                <div class="text-subtitle1 text-weight-bolder text-dark line-height-1 ellipsis">
                  League Standings
                </div>
                <div class="text-caption text-grey-6 text-uppercase letter-spacing-1">
                  Current overview
                </div>
              </div>
            </div>
          </q-card-section>

          <q-card-section class="q-pt-sm">
            <LeagueStandings :league-id="leagueId" />
          </q-card-section>
        </q-card>
      </div>

      <!-- Results: grouped together in their own grid, next to the standings box -->
      <div :class="showStandings ? 'col-12 col-md-8 col-lg-9' : 'col-12'">
        <div class="game-cards-grid">
          <div
            v-for="game in selectedGamesWithResults"
            :key="game.id"
          >
            <q-card flat bordered class="match-game-card">
              <q-card-section class="q-pb-none">
                <div class="row items-center no-wrap">
                  <div class="game-icon-box q-mr-sm">
                    <q-icon name="sports_esports" color="primary" size="24px" />
                  </div>
                  <div class="column col">
                    <div class="text-subtitle1 text-weight-bolder text-dark line-height-1 ellipsis">
                      {{ game.game_name }}
                    </div>
                    <div class="text-caption text-grey-6 text-uppercase letter-spacing-1">
                      Selected by {{ game.selected_by }}
                    </div>
                  </div>
                  <q-badge
                    v-if="getWinConditionName(game.id)"
                    color="indigo-1"
                    text-color="indigo-8"
                    class="stat-badge elegant-badge q-ml-sm"
                  >
                    <q-icon name="flag_circle" size="14px" class="q-mr-xs shrink-0" />
                    <span class="ellipsis">{{ getWinConditionName(game.id) }}</span>
                    <KennerTooltip>
                      <span class="text-weight-bold">Win condition:</span>
                      {{ getWinConditionName(game.id) }}
                    </KennerTooltip>
                  </q-badge>
                </div>
              </q-card-section>

              <q-card-section class="q-pt-sm">
                 <MatchResult
                   :selected-game="game"
                   :display-game-name="false"
                   :match-results="matchResultsBySelectedGame"
                 />
              </q-card-section>
            </q-card>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useLeagueStore } from 'stores/leagueStore';
import { storeToRefs } from 'pinia';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import MatchResult from 'components/league/MatchResult.vue';
import LeagueStandings from 'components/league/LeagueStandings.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';

const props = defineProps<{
  leagueId: number;
  showStandings?: boolean;
}>();

const leagueStore = useLeagueStore(props.leagueId)();
const {
  loading,
  selectedGamesWithResults,
  matchResultsBySelectedGame,
  initialized
} = storeToRefs(leagueStore);

function getWinConditionName(selectedGameId: number): string | null {
  const results = matchResultsBySelectedGame.value?.[selectedGameId];
  return results?.[0]?.win_condition?.name ?? null;
}

onMounted(async () => {
  if (!initialized.value) {
    await leagueStore.init();
  }
});
</script>

<style scoped lang="scss">
.stat-badge {
  padding: 4px 8px;
  font-size: 11px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  font-weight: 500;
  max-width: 100%;
}

.elegant-badge {
  border: 1px solid rgba(0, 0, 0, 0.06);
  backdrop-filter: blur(4px);
}
.match-game-card {
  border-radius: 12px;
  background: #fff;
}

.game-cards-grid {
  display: grid;
  // `auto-fit` collapses empty tracks so a single result fills the row instead
  // of leaving a phantom column, and `min(100%, 360px)` lets cards shrink below
  // 360px on narrow columns so the grid never overflows the league container.
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 360px), 1fr));
  gap: 16px;
  width: 100%;
  min-width: 0;
  align-items: start;
}

.standings-card {
  background: rgba(var(--q-primary), 0.03);
}

.game-icon-box {
  background: rgba(var(--q-primary), 0.1);
  padding: 8px;
  border-radius: 10px;
}

.line-height-1 {
  line-height: 1.1;
}

.letter-spacing-1 {
  letter-spacing: 1px;
}

.border-subtle {
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.opacity-20 {
  opacity: 0.2;
}
</style>

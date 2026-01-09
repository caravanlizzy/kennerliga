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

    <div v-else class="row q-col-gutter-md">
      <div
        v-for="game in selectedGamesWithResults"
        :key="game.id"
        class="col-12 col-md-6 col-lg-4"
      >
        <q-card flat bordered class="match-game-card full-height">
          <q-card-section class="q-pb-none">
            <div class="row items-center no-wrap">
              <div class="game-icon-box q-mr-sm">
                <q-icon name="sports_esports" color="primary" size="24px" />
              </div>
              <div class="column">
                <div class="text-subtitle1 text-weight-bolder text-dark line-height-1 ellipsis">
                  {{ game.game_name }}
                </div>
                <div class="text-caption text-grey-6 text-uppercase letter-spacing-1">
                  Selected by {{ game.selected_by }}
                </div>
              </div>
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
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useLeagueStore } from 'stores/leagueStore';
import { storeToRefs } from 'pinia';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import MatchResult from 'components/league/MatchResult.vue';

const props = defineProps<{
  leagueId: number;
}>();

const leagueStore = useLeagueStore(props.leagueId)();
const {
  loading,
  selectedGamesWithResults,
  matchResultsBySelectedGame,
  initialized
} = storeToRefs(leagueStore);

onMounted(async () => {
  if (!initialized.value) {
    await leagueStore.updateLeagueData();
  }
});
</script>

<style scoped lang="scss">
.match-game-card {
  transition: all 0.3s ease;
  border-radius: 12px;
  background: #fff;
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

<template>
  <q-page>
    <div v-if="loading || !user" class="q-pa-md">
      <LoadingSpinner text="Loading league data...">
        <template #skeleton>
          <q-skeleton type="rect" height="28px" class="q-mb-sm" />
          <q-skeleton type="text" class="q-mb-xs" />
          <q-skeleton type="text" width="70%" class="q-mb-md" />

          <div class="row q-col-gutter-md">
            <div
              v-for="n in 4"
              :key="n"
              class="col-12 col-sm-6 col-md-4 col-lg-3"
            >
              <q-skeleton height="160px" square />
            </div>
          </div>
        </template>
      </LoadingSpinner>
    </div>

    <div v-else class="q-pa-md relative-position league-page">
      <ActionBar class="q-mb-md" />

      <LeagueStandingsSection />
      <GameSelectionSection />
      <BanGameSection />
      <ResultsSection />
      <ReportResultsSection />
      <PlayersSection />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue';
import { storeToRefs } from 'pinia';
import ActionBar from 'components/ui/ActionBar.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import LeagueStandingsSection from 'components/league/sections/LeagueStandingsSection.vue';
import GameSelectionSection from 'components/league/sections/GameSelectionSection.vue';
import BanGameSection from 'components/league/sections/BanGameSection.vue';
import ResultsSection from 'components/league/sections/ResultsSection.vue';
import ReportResultsSection from 'components/league/sections/ReportResultsSection.vue';
import PlayersSection from 'components/league/sections/PlayersSection.vue';
import { useUserStore } from 'stores/userStore';
import { useUpdateStore } from 'stores/updateStore';
import { useMyLeagueStore } from 'src/composables/myLeague';

const { user } = storeToRefs(useUserStore());
const myLeagueStore = useMyLeagueStore();
const { loading } = storeToRefs(myLeagueStore);

const updateStore = useUpdateStore();
let unsubscribe: () => void;

onMounted(async () => {
  await myLeagueStore.init();

  unsubscribe = updateStore.subscribe('/league/', async () => {
    await myLeagueStore.refresh();
  });
});

onUnmounted(() => {
  if (unsubscribe) {
    unsubscribe();
  }
});
</script>

<style scoped>
.league-page {
  /* Layout container for league sections. */
}
</style>

<template>
  <q-page>
    <div v-if="loading || !user" class="q-py-md">
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

    <div v-else class="q-py-md relative-position league-page">
      <div class="unified-content-container">
        <BanGameSection flat no-margin />
        <div v-if="leagueStatus === 'BANNING'" class="section-divider" />
        <LeagueStandingsSection flat no-margin />
        <div class="section-divider" />

        <GameSelectionSection flat no-margin />

        <div
          v-if="leagueStatus === 'PLAYING' || leagueStatus === 'DONE'"
          class="section-divider"
        />
        <ResultsSection flat no-margin />

        <div
          v-if="leagueStatus === 'PLAYING'"
          class="section-divider"
        />
        <ReportResultsSection flat no-margin />

        <div class="section-divider" />
        <PlayersSection flat no-margin />
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue';
import { storeToRefs } from 'pinia';
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
const { loading, leagueStatus } = storeToRefs(myLeagueStore);

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

<style scoped lang="scss">
.league-page {
  /* Layout container for league sections. */
  max-width: 1200px;
  margin: 0 auto;
}

.unified-content-container {
  background: white;
  border-radius: var(--kenner-card-radius);
  border: 1px solid var(--kenner-border-color);
  box-shadow: var(--kenner-card-shadow);
  overflow: hidden;
  padding: 0 24px;

  @media (max-width: 599px) {
    padding: 0 16px;
    border-radius: 12px;
  }

  /* Make sure the first and last section feel integrated */
  & > :first-child :deep(.content-section-container) {
    padding-top: 24px !important;
    @media (max-width: 599px) {
      padding-top: 20px !important;
    }
  }

  & > :last-child :deep(.content-section-container) {
    padding-bottom: 32px !important;
    @media (max-width: 599px) {
      padding-bottom: 24px !important;
    }
  }

  & > .section-divider:first-child,
  & > .section-divider:last-child {
    display: none;
  }

  & > .section-divider + .section-divider {
    display: none;
  }
}

.section-divider {
  height: 1px;
  background: rgba(0, 0, 0, 0.05);
  margin: 0 -24px;
  opacity: 0.6;

  @media (max-width: 599px) {
    margin: 0 -16px;
  }
}
</style>

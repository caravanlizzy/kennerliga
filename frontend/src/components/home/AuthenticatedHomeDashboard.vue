<template>
  <div class="column col q-pt-none">
    <div class="row q-col-gutter-md">
      <!-- Left Column: Primary Info -->
      <div class="col-12 col-md-8">
        <HomeSeasonSection
          v-model:selectedSeasonYear="selectedSeasonYear"
          v-model:selectedSeasonMonth="selectedSeasonMonth"
          :selected-season-id="selectedSeasonId"
          :current-season-id="currentSeasonId"
          :season-year-options="seasonYearOptions"
          :season-month-options="seasonMonthOptions"
          :loading="loading"
          :refreshing="refreshing"
        />

        <HomeLeaderboardSection
          v-model:year="selectedYear"
          :years="availableYears"
          class="q-mt-md"
        />
      </div>

      <!-- Right Column: Secondary Info -->
      <div class="col-12 col-md-4">
        <HomeLiveActionSection />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'AuthenticatedHomeDashboard' });
import { onMounted, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { useUserStore } from 'stores/userStore';
import { useHomeSeasonStore } from 'stores/homeSeasonStore';
import HomeSeasonSection from 'components/home/HomeSeasonSection.vue';
import HomeLeaderboardSection from 'components/home/HomeLeaderboardSection.vue';
import HomeLiveActionSection from 'components/home/HomeLiveActionSection.vue';

const { isAuthenticated } = storeToRefs(useUserStore());

// Season selection state now lives in a Pinia store, so it persists across
// navigation. Re-mounting this component reuses the cached data and only
// triggers a non-blocking background refresh — no more spinner on every visit.
const homeSeasonStore = useHomeSeasonStore();
const {
  selectedYear,
  availableYears,
  loading,
  refreshing,
  selectedSeasonYear,
  selectedSeasonMonth,
  selectedSeasonId,
  currentSeasonId,
  seasonYearOptions,
  seasonMonthOptions,
} = storeToRefs(homeSeasonStore);

function ensureInitialized() {
  if (isAuthenticated.value) {
    // `init` is stale-while-revalidate: blocking on first call, background
    // refresh on subsequent ones.
    void homeSeasonStore.init();
  }
}

onMounted(ensureInitialized);

// If the user logs in after mount, initialize; if they log out, drop the cache.
watch(isAuthenticated, (isAuth, wasAuth) => {
  if (isAuth && !wasAuth) ensureInitialized();
  else if (!isAuth && wasAuth) homeSeasonStore.reset();
});
</script>

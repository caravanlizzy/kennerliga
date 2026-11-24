<template>
  <div class="column col q-pt-none">
    <!-- Hero Greeting & Quick Action Hub -->
    <HomeHeroGreeting
      @select-current-season="homeSeasonStore.selectCurrentSeason"
    />

    <div class="row q-col-gutter-md">
      <!-- Left Column: Primary Info with Segmented Toggle -->
      <div class="col-12 col-md-8">
        <div class="row items-center justify-between q-mb-sm">
          <SmoothSwitch
            v-model="activeTab"
            :options="[
              { label: 'Current Season', value: 'season', icon: 'military_tech' },
              { label: 'Hall of Fame', value: 'leaderboard', icon: 'stars' },
            ]"
          />
        </div>

        <HomeSeasonSection
          v-show="activeTab === 'season'"
          v-model:selectedSeasonYear="selectedSeasonYear"
          v-model:selectedSeasonMonth="selectedSeasonMonth"
          :selected-season-id="selectedSeasonId"
          :current-season-id="currentSeasonId"
          :season-year-options="seasonYearOptions"
          :season-month-options="seasonMonthOptions"
          :loading="loading"
          :refreshing="refreshing"
          @select-current-season="homeSeasonStore.selectCurrentSeason"
        />

        <HomeLeaderboardSection
          v-show="activeTab === 'leaderboard'"
          v-model:year="selectedYear"
          :years="availableYears"
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
import { ref, onMounted, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { useUserStore } from 'stores/userStore';
import { useHomeSeasonStore } from 'stores/homeSeasonStore';
import HomeHeroGreeting from 'components/home/HomeHeroGreeting.vue';
import SmoothSwitch from 'components/base/SmoothSwitch.vue';
import HomeSeasonSection from 'components/home/HomeSeasonSection.vue';
import HomeLeaderboardSection from 'components/home/HomeLeaderboardSection.vue';
import HomeLiveActionSection from 'components/home/HomeLiveActionSection.vue';

const { isAuthenticated } = storeToRefs(useUserStore());

const activeTab = ref<'season' | 'leaderboard'>('season');

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

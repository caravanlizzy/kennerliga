<template>
  <div class="column col q-pt-none">
    <!-- Hero Greeting & Quick Action Hub -->
    <HomeHeroGreeting />

    <div class="row q-col-gutter-md items-stretch">
      <!-- Left Column: Primary Info -->
      <div class="col-12 col-md-8 column">
        <HomeSeasonSection
          v-model:selectedSeasonYear="selectedSeasonYear"
          v-model:selectedSeasonMonth="selectedSeasonMonth"
          :selected-season-id="selectedSeasonId"
          :current-season-id="currentSeasonId"
          :season-year-options="seasonYearOptions"
          :season-month-options="seasonMonthOptions"
          :loading="loading"
          :refreshing="refreshing"
          class="col full-height"
          @select-current-season="homeSeasonStore.selectCurrentSeason"
        />
      </div>

      <!-- Right Column: Secondary Info -->
      <div class="col-12 col-md-4 column">
        <HomeLiveActionSection class="col full-height" />
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
import HomeHeroGreeting from 'components/home/HomeHeroGreeting.vue';
import HomeSeasonSection from 'components/home/HomeSeasonSection.vue';
import HomeLiveActionSection from 'components/home/HomeLiveActionSection.vue';

const { isAuthenticated } = storeToRefs(useUserStore());

// Season selection state lives in a Pinia store, persisting across navigation.
// Re-mounting this component reuses cached data with background refresh.
const homeSeasonStore = useHomeSeasonStore();
const {
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

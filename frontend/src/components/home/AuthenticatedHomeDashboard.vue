<template>
  <div class="column col q-pt-none">
    <div class="row q-col-gutter-xl">
      <!-- Left Column: Primary Info -->
      <div class="col-12 col-md-8">
        <HomeSeasonSection
          v-model:selectedSeasonYear="selectedSeasonYear"
          v-model:selectedSeasonMonth="selectedSeasonMonth"
          :selected-season-id="selectedSeasonId"
          :season-year-options="seasonYearOptions"
          :season-month-options="seasonMonthOptions"
          :loading="loadingSeasonInit"
        />

        <HomeLeaderboardSection
          v-model:year="selectedYear"
          :years="availableYears"
          class="q-mt-xl"
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
import { onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useUserStore } from 'stores/userStore';
import { useHomeSeasonSelection } from 'src/composables/useHomeSeasonSelection';
import HomeSeasonSection from 'components/home/HomeSeasonSection.vue';
import HomeLeaderboardSection from 'components/home/HomeLeaderboardSection.vue';
import HomeLiveActionSection from 'components/home/HomeLiveActionSection.vue';

const { isAuthenticated } = storeToRefs(useUserStore());

const {
  selectedYear,
  availableYears,
  loadingSeasonInit,
  selectedSeasonYear,
  selectedSeasonMonth,
  selectedSeasonId,
  seasonYearOptions,
  seasonMonthOptions,
  initSeasonSelection,
} = useHomeSeasonSelection(isAuthenticated);

onMounted(initSeasonSelection);
</script>

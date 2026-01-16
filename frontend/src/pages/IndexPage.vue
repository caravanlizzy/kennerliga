<template>
  <q-page class="column col q-pa-none">
    <div class="row">
      <AnnouncementDisplay class="col-12 q-px-md" />
    </div>

    <div class="q-pa-md q-mx-auto" style="max-width: 1300px; width: 100%">
      <WelcomeSection
        v-if="!isMobile || mobileContent === 'welcome'"
        :is-authenticated="isAuthenticated"
      />

      <template v-if="isAuthenticated">
        <div
          v-if="isMobile && user?.myCurrentLeagueId"
          class="row justify-center q-pt-sm q-px-md"
        >
          <NavMyLeague />
        </div>

        <div v-if="!isMobile" class="column col q-pt-none">
          <div class="row col">
            <div class="col-12 col-md">
              <ContentSection
                id="seasons"
                icon="military_tech"
                :bordered="false"
                title="Seasons"
                class="col-12 q-mt-none"
                color="primary"
              >
                <template #header-extra>
                  <div
                    v-if="!loadingSeasonInit"
                    class="row no-wrap q-gutter-x-sm q-ml-md"
                  >
                    <div style="width: 110px">
                      <KennerSelect
                        v-model="selectedSeasonYear"
                        :options="seasonYearOptions"
                        label="Year"
                        emit-value
                        map-options
                      />
                    </div>
                    <div style="width: 110px">
                      <KennerSelect
                        v-model="selectedSeasonMonth"
                        :options="seasonMonthOptions"
                        label="Month"
                        emit-value
                        map-options
                      />
                    </div>
                  </div>
                </template>
                <SeasonStandings
                  v-if="!loadingSeasonInit"
                  :seasonId="selectedSeasonId"
                  class="col-12"
                />
                <div v-else class="flex flex-center q-pa-xl">
                  <LoadingSpinner text="Initializing seasons..." />
                </div>
              </ContentSection>
              <ContentSection
                v-if="isAuthenticated"
                id="live-action"
                title="Live Action"
                icon="bolt"
                color="accent"
                :bordered="false"
                class="col-12 q-mt-md"
              >
                <LiveActionFeed />
              </ContentSection>
              <ContentSection
                :bordered="false"
                id="leaderboard"
                icon="stars"
                title="Leaderboard"
                class="col-12 q-mt-md"
                color="warning"
              >
                <template #header-extra>
                  <div style="min-width: 120px" class="q-ml-md">
                    <KennerSelect
                      v-model="selectedYear"
                      :options="availableYears"
                      emit-value
                      map-options
                    />
                  </div>
                </template>
                <LeaderBoard :year="selectedYear" />
              </ContentSection>
            </div>
          </div>
        </div>
      </template>
    </div>
  </q-page>
</template>

<script setup lang="ts">
defineOptions({ name: 'IndexPage' });
import NavMyLeague from 'src/components/nav/NavMyLeague.vue';
import LiveActionFeed from 'components/ui/LiveActionFeed.vue';
import SeasonStandings from 'components/season/SeasonStandings.vue';
import AnnouncementDisplay from 'components/ui/AnnouncementDisplay.vue';
import { useResponsive } from 'src/composables/responsive';
import LeaderBoard from 'components/season/LeaderBoard.vue';
import ContentSection from 'components/base/ContentSection.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import { useRoute } from 'vue-router';
import { computed, onMounted, ref, watch } from 'vue';
import WelcomeSection from 'components/home/WelcomeSection.vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import {
  fetchAvailableYears,
  fetchCurrentSeasonId,
  fetchSeason,
  fetchSeasons,
} from 'src/services/seasonService';
import type { TSeasonDto } from 'src/types';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';

const { isMobile } = useResponsive();
const { isAuthenticated } = storeToRefs(useUserStore());
const { user } = storeToRefs(useUserStore());
const route = useRoute();

const mobileContent = computed(() => {
  if (route.name === 'home') return 'welcome';
  return null;
});

const selectedYear = ref(new Date().getFullYear());
const availableYears = ref<number[]>([]);
const loadingSeasonInit = ref(false);

// Seasons logic
const seasonsForYear = ref<TSeasonDto[]>([]);
const selectedSeasonYear = ref<number | null>(null);
const selectedSeasonMonth = ref<number | null>(null);

const seasonYearOptions = computed(() =>
  [...availableYears.value]
    .sort((a, b) => b - a)
    .map((y) => ({ label: String(y), value: y }))
);

const seasonMonthOptions = computed(() => {
  return seasonsForYear.value
    .map((s) => s.month)
    .sort((a, b) => a - b)
    .map((m) => ({
      label: m,
      value: m,
    }));
});

const selectedSeasonId = computed(() => {
  const found = seasonsForYear.value.find(
    (s) => s.month === selectedSeasonMonth.value
  );
  return found ? found.id : null;
});

watch(selectedSeasonYear, async (newYear) => {
  if (newYear) {
    const seasons = await fetchSeasons({ year: newYear });
    seasonsForYear.value = seasons;

    // If current selected month is not in new seasons, pick the latest month
    if (seasons.length > 0) {
      const months = seasons.map((s) => s.month);
      if (
        !selectedSeasonMonth.value ||
        !months.includes(selectedSeasonMonth.value)
      ) {
        selectedSeasonMonth.value = Math.max(...months);
      }
    } else {
      selectedSeasonMonth.value = null;
    }
  } else {
    seasonsForYear.value = [];
    selectedSeasonMonth.value = null;
  }
});

onMounted(async () => {
  if (isAuthenticated.value) {
    loadingSeasonInit.value = true;
    try {
      // 1. Fetch current season ID first as requested
      const currentSeasonId = await fetchCurrentSeasonId();

      // 2. Then fetch years and seasons
      availableYears.value = await fetchAvailableYears();

      if (currentSeasonId) {
        const season = await fetchSeason(currentSeasonId);
        if (season) {
          selectedYear.value = season.year;

          seasonsForYear.value = await fetchSeasons({ year: season.year });

          selectedSeasonYear.value = season.year;
          selectedSeasonMonth.value = season.month;
        }
      } else if (availableYears.value.length > 0) {
        const year = availableYears.value[0];
        selectedYear.value = year;

        const seasons = await fetchSeasons({ year });
        seasonsForYear.value = seasons;

        selectedSeasonYear.value = year;
        if (seasons.length > 0) {
          selectedSeasonMonth.value = Math.max(...seasons.map(s => s.month));
        }
      }
    } finally {
      loadingSeasonInit.value = false;
    }
  }
});
</script>

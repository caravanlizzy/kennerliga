<template>
  <q-page class="column col q-pa-md">
    <WelcomeSection v-if="!isMobile" :is-authenticated="isAuthenticated" />

    <template v-if="isAuthenticated">
      <AnnouncementDisplay class="col-auto" />
      <div v-if="isMobile" class="column col">
        <div class="col column">
          <WelcomeSection
            v-if="mobileContent === 'welcome'"
            :is-authenticated="isAuthenticated"
            key="welcome"
          />

          <ScrollContainer v-else-if="mobileContent === 'seasons'" key="seasons">
            <div class="full-height">
              <div
                class="q-pa-md row items-center justify-between no-wrap border-bottom-subtle"
              >
                <div class="text-h5 text-weight-bold text-dark">Seasons</div>
                <div class="row no-wrap q-gutter-x-xs">
                  <div style="width: 110px">
                    <KennerSelect
                      v-model="selectedSeasonYear"
                      :options="seasonYearOptions"
                      dense
                      label="Year"
                      emit-value
                      map-options
                    />
                  </div>
                  <div style="width: 110px">
                    <KennerSelect
                      v-model="selectedSeasonMonth"
                      :options="seasonMonthOptions"
                      dense
                      label="Month"
                      emit-value
                      map-options
                    />
                  </div>
                </div>
              </div>
              <SeasonStandings :seasonId="selectedSeasonId" />
            </div>
          </ScrollContainer>

          <ScrollContainer v-else-if="mobileContent === 'live'" key="live">
            <div class="q-px-md">
              <ContentSection
                v-if="isAuthenticated"
                id="live-action-mobile"
                title="Live Action"
                icon="bolt"
                color="accent"
                :bordered="false"
              >
                <LiveActionFeed />
              </ContentSection>
            </div>
          </ScrollContainer>
          <ScrollContainer v-else-if="mobileContent === 'leaderboard'" key="leaderboard">
            <div class="full-height">
              <div
                class="q-pa-md row items-center justify-between no-wrap border-bottom-subtle"
              >
                <div class="text-h5 text-weight-bold text-dark">
                  Leaderboard
                </div>
                <div style="min-width: 100px">
                  <KennerSelect
                    v-model="selectedYear"
                    :options="availableYears"
                    class="full-width"
                    emit-value
                    map-options
                  />
                </div>
              </div>
              <LeaderBoard :year="selectedYear" />
            </div>
          </ScrollContainer>

          <div v-else-if="mobileContent === 'chat'" class="col column" key="chat">
            <div class="q-pa-md row items-center border-bottom-subtle bg-white">
              <q-icon name="chat" color="blue-grey-8" size="sm" class="q-mr-sm" />
              <div class="text-h5 text-weight-bold">KennerChat</div>
            </div>
            <KennerChat class="col bg-white" />
          </div>
        </div>
      </div>
      <div v-else class="column col q-pt-none">
        <div class="row col">
          <div class="col-12 col-md">
            <ContentSection
              id="seasons"
              icon="military_tech"
              :bordered="false"
              title="Seasons"
              class="col-12"
              color="primary"
            >
              <template #header-extra>
                <div class="row no-wrap q-gutter-x-sm q-ml-md">
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
              <SeasonStandings :seasonId="selectedSeasonId" class="col-12" />
            </ContentSection>
            <ContentSection
              v-if="isAuthenticated"
              id="live-action"
              title="Live Action"
              icon="bolt"
              color="accent"
              :bordered="false"
              class="col-12"
            >
              <LiveActionFeed />
            </ContentSection>
            <ContentSection
              :bordered="false"
              id="leaderboard"
              icon="stars"
              title="Leaderboard"
              class="col-12"
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
      <div class="q-py-xl"></div>
    </template>
    <template v-else>
      <div v-if="isMobile" class="column col">
        <WelcomeSection :is-authenticated="false" />
      </div>
    </template>
  </q-page>
</template>

<script setup lang="ts">
import KennerChat from 'components/chat/KennerChat.vue';
import LiveActionFeed from 'components/ui/LiveActionFeed.vue';
import SeasonStandings from 'components/season/SeasonStandings.vue';
import AnnouncementDisplay from 'components/ui/AnnouncementDisplay.vue';
import { useResponsive } from 'src/composables/responsive';
import LeaderBoard from 'components/season/LeaderBoard.vue';
import ContentSection from 'components/base/ContentSection.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import { useQuasar } from 'quasar';
import { computed, onMounted, ref, watch } from 'vue';
import WelcomeSection from 'components/home/WelcomeSection.vue';
import ScrollContainer from 'components/base/ScrollContainer.vue';
import { useUserStore } from 'stores/userStore';
import { useUiStore } from 'src/stores/uiStore';
import { storeToRefs } from 'pinia';
import {
  fetchAvailableYears,
  fetchCurrentSeasonId,
  fetchSeason,
  fetchSeasons,
} from 'src/services/seasonService';
import type { TSeasonDto } from 'src/types';

const { isMobile } = useResponsive();
const { isAuthenticated } = storeToRefs(useUserStore());
const uiStore = useUiStore();
const { activeTab: mobileContent } = storeToRefs(uiStore);

const selectedYear = ref(new Date().getFullYear());
const availableYears = ref<number[]>([]);

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
    const [years, currentSeasonId] = await Promise.all([
      fetchAvailableYears(),
      fetchCurrentSeasonId(),
    ]);

    availableYears.value = years;

    if (currentSeasonId) {
      const season = await fetchSeason(currentSeasonId);
      if (season) {
        selectedYear.value = season.year;
        // Setting this will trigger the watcher which fetches seasons and sets month
        selectedSeasonYear.value = season.year;
        // Explicitly set month after a short delay or by waiting for the fetch
        // But actually, we already have the season object, so we can just set it
        // The watcher might overwrite it, so we should be careful.
        // Let's just set it and ensure the watcher doesn't overwrite it if it's already set to a valid value.
        selectedSeasonMonth.value = season.month;
      }
    } else if (availableYears.value.length > 0) {
      selectedYear.value = availableYears.value[0];
      selectedSeasonYear.value = availableYears.value[0];
    }
  }
});
</script>

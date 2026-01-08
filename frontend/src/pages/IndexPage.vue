<template>
  <q-page class="column col q-pa-md">
    <WelcomeSection v-if="!isMobile" :is-authenticated="isAuthenticated" />

    <template v-if="isAuthenticated">
      <AnnouncementDisplay class="col-auto" />
      <div v-if="isMobile" class="column col">
        <div class="col column">
          <WelcomeSection v-if="mobileContent === 'welcome'" :is-authenticated="isAuthenticated" />
          <KennerChat v-else-if="mobileContent === 'chat'" class="column" />

          <ScrollContainer v-else-if="mobileContent === 'seasons'">
            <div class="bg-grey-1 full-height">
              <SeasonStandings />
            </div>
          </ScrollContainer>

          <ScrollContainer v-else-if="mobileContent === 'live'">
            <ContentSection
              v-if="isAuthenticated"
              id="live-action-mobile"
              title="Live Action"
              icon="sensors"
              color="accent"
              :bordered="false"
              class="q-my-md"
            >
              <LiveActionFeed />
            </ContentSection>
          </ScrollContainer>
          <ScrollContainer v-else-if="mobileContent === 'leaderboard'">
            <div class="bg-grey-1 full-height">
              <div class="q-pa-md row items-center justify-between no-wrap">
                <div class="text-h5 text-weight-bold text-dark">Leaderboard</div>
                <div style="min-width: 120px">
                  <KennerSelect
                    v-model="selectedYear"
                    :options="availableYears"
                    dense
                    class="full-width"
                  />
                </div>
              </div>
              <LeaderBoard :year="selectedYear" />
            </div>
          </ScrollContainer>
        </div>
      </div>
      <div v-else class="column col q-pt-none">
        <div class="row col">
          <div class="col-12 col-md">
            <ContentSection
              id="seasons"
              icon="history"
              minimizable
              :bordered="false"
              title="Seasons"
              class="col-12"
              color="primary"
            >
              <SeasonStandings class="col-12" />
            </ContentSection>
            <div v-if="!isLiveActionVisible" class="row justify-end q-mb-sm">
              <q-btn
                flat
                dense
                round
                color="accent"
                icon="sensors"
                @click="isLiveActionVisible = true"
              >
                <q-tooltip>Show Live Action</q-tooltip>
              </q-btn>
            </div>
            <ContentSection
              v-if="isAuthenticated && isLiveActionVisible"
              id="live-action"
              title="Live Action"
              icon="sensors"
              color="accent"
              minimizable
              :bordered="false"
              class="col-12"
            >
              <LiveActionFeed />
            </ContentSection>
            <ContentSection
              :bordered="false"
              id="leaderboard"
              icon="leaderboard"
              minimizable
              title="Leaderboard"
              class="col-12"
              color="primary"
            >
              <template #header-extra>
                <div style="min-width: 120px" class="q-ml-md">
                  <KennerSelect
                    v-model="selectedYear"
                    :options="availableYears"
                    dense
                    filled
                    square
                    size="sm"
                    :dark="$q.dark.isActive"
                  />
                </div>
              </template>
              <LeaderBoard :year="selectedYear" />
            </ContentSection>
          </div>
        </div>
      </div>
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
import { onMounted, ref, watch } from 'vue';
import WelcomeSection from 'components/home/WelcomeSection.vue';
import ScrollContainer from 'components/base/ScrollContainer.vue';
import { useUserStore } from 'stores/userStore';
import { useUiStore } from 'src/stores/uiStore';
import { storeToRefs } from 'pinia';
import {
  fetchAvailableYears,
  fetchCurrentSeasonId,
  fetchSeason,
} from 'src/services/seasonService';

const { isMobile } = useResponsive();
const { isAuthenticated } = storeToRefs(useUserStore());
const uiStore = useUiStore();
const { activeTab: mobileContent } = storeToRefs(uiStore);
const $q = useQuasar();
const isMdUp = $q.screen.gt.sm;
const isLiveActionVisible = ref(
  $q.localStorage.getItem('isLiveActionVisible') !== false
);

watch(isLiveActionVisible, (val) => {
  $q.localStorage.set('isLiveActionVisible', val);
});

const selectedYear = ref(new Date().getFullYear());
const availableYears = ref<number[]>([]);

onMounted(async () => {
  if (isAuthenticated) {
    availableYears.value = await fetchAvailableYears();
    const currentSeasonId = await fetchCurrentSeasonId();
    if (currentSeasonId) {
      const season = await fetchSeason(currentSeasonId);
      if (season) {
        selectedYear.value = season.year;
      }
    } else if (availableYears.value.length > 0) {
      selectedYear.value = availableYears.value[0];
    }
  }
});
</script>

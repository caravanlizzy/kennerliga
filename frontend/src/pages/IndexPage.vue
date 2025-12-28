<template>
  <q-page class="column col">
    <template v-if="!isAuthenticated">
      <div class="flex flex-center col q-pa-lg text-center">
        <div style="max-width: 400px">
          <q-icon name="lock" size="100px" color="grey-5" class="q-mb-md" />
          <div class="text-h4 text-weight-bold q-mb-md">Registered Only</div>
          <div class="text-subtitle1 text-grey-8 q-mb-xl">
            This site contains private content. Please sign in or create an
            account to access the seasons, chat, and leaderboards.
          </div>
          <div class="row q-gutter-md justify-center">
            <KennerButton color="primary" label="Login" icon="login" to="/login" />
          </div>
        </div>
      </div>
    </template>
    <template v-else>
      <AnnouncementDisplay class="col-auto" />
      <div v-if="isMobile" class="column col">
        <div class="col column">
          <KennerChat v-if="mobileContent === 'chat'" class="column" />

<!--          <SeasonWinners v-else-if="mobileContent === 'pokal'" class="q-pa-md" />-->

          <ScrollContainer v-else-if="mobileContent === 'live'">
            <ContentSection
              v-if="isAuthenticated"
              title="Live Action"
              color="accent"
              :bordered="false"
              class="q-mx-md q-mt-md"
            >
              <LiveActionFeed />
            </ContentSection>
          </ScrollContainer>

          <ScrollContainer v-else-if="mobileContent === 'seasons'">
            <SeasonStandings />
          </ScrollContainer>
          <ScrollContainer v-else-if="mobileContent === 'leaderboard'">
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
          </ScrollContainer>
        </div>
        <q-toolbar class="col-auto bg-grey-4 text-primary flex-center">
          <q-tabs switch-indicator v-model="mobileContent" class="full-width">
            <q-tab icon="bolt" name="live" label="Live" />
            <q-tab icon="history" name="seasons" label="Season" />
            <q-tab icon="chat" name="chat" label="Chat" />
<!--            <q-tab icon="emoji_events" name="pokal" label="Winners" />-->
            <q-tab icon="leaderboard" name="leaderboard" label="Rank" />
          </q-tabs>
        </q-toolbar>
      </div>
      <div v-else class="column col q-pa-md">
        <div class="row col">
          <div class="col-12 col-md" :class="{ 'q-pr-lg': isMdUp }">
            <ContentSection
              v-if="isAuthenticated"
              title="Live Action"
              color="accent"
              :bordered="false"
              class="col-12 q-mb-md"
            >
              <LiveActionFeed />
            </ContentSection>
            <ContentSection
              titleEnd
              :bordered="false"
              title="Seasons"
              class="col-12"
              color="dark"
            >
              <SeasonStandings class="col-12" />
            </ContentSection>
            <ContentSection
              :bordered="false"
              titleEnd
              title=""
              class="col-12"
              color="dark"
            >
              <template #title>
                <div style="min-width: 120px">
                  <KennerSelect
                    v-model="selectedYear"
                    :options="availableYears"
                    dense
                    filled
                    square
                    size="sm"
                    class="q-ml-md"
                    :dark="$q.dark.isActive"
                  />
                </div>
              </template>
              <template #header-extra>
                <div class="q-ml-md">Leaderboard</div>
              </template>
              <LeaderBoard :year="selectedYear" />
            </ContentSection>
          </div>
          <ContentSection
            class="col-12 col-md-auto column bg-grey-2"
            bordered
            title="Kennerchat"
            color="dark"
            style="max-height: calc(100vh - 200px); position: sticky; top: 100px"
          >
            <KennerChat class="col" />
          </ContentSection>
        </div>
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
import { onMounted, ref } from 'vue';
import ScrollContainer from 'components/base/ScrollContainer.vue';
import { useUserStore } from 'stores/userStore';
import { fetchAvailableYears } from 'src/services/seasonService';
import KennerButton from 'components/base/KennerButton.vue';

const { isMobile } = useResponsive();
const { isAuthenticated } = useUserStore();
const $q = useQuasar();
const isMdUp = $q.screen.gt.sm;

const mobileContent = ref('seasons');
const selectedYear = ref(new Date().getFullYear());
const availableYears = ref<number[]>([]);

onMounted(async () => {
  if (isAuthenticated) {
    availableYears.value = await fetchAvailableYears();
    if (availableYears.value.length > 0) {
      selectedYear.value = availableYears.value[0];
    }
  }
});
</script>

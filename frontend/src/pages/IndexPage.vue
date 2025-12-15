<template>
  <q-page class="column col">
    <AnnouncementDisplay class="col-auto" />
    <div v-if="isMobile" class="column col">
      <div class="col column">
        <KennerChat v-if="mobileContent === 'chat'" class="column"/>
        <ScrollContainer v-else-if="mobileContent === 'seasons'">
          <SeasonStandings  />
        </ScrollContainer>
        <ScrollContainer v-else-if="mobileContent === 'yearly'">
          <YearStandings :year="2023"/>
        </ScrollContainer>
      </div>
      <q-toolbar class="col-auto bg-primary text-secondary">
        <q-tabs v-model="mobileContent">
          <q-tab icon="chat" name="chat" label="Chat" />
          <q-tab icon="history" name="seasons" label="Season" />
          <q-tab icon="year" name="yearly" label="Year" />
        </q-tabs>
      </q-toolbar>
    </div>
    <div v-else class="column col q-pa-md">
      <div class="row col">
        <div class="col-12 col-md" :class="{ 'q-pr-lg': isMdUp }">
          <ContentSection
            :isOpened="true"
            titleEnd
            :bordered="false"
            title="Seasons"
            color="dark"
          >
            <SeasonStandings class="col-12" />
          </ContentSection>
          <ContentSection
            :bordered="false"
            titleEnd
            title="Year Standings"
            class="col-12"
            color="dark"
          >
            <YearStandings :year="2023" />
          </ContentSection>
        </div>
        <ContentSection
          class="col-12 col-md-auto column bg-grey-2"
          isOpened
          bordered
          title="Kennerchat"
          color="dark"
        >
          <KennerChat class="col" />
        </ContentSection>
      </div>
    </div>
  </q-page>

</template>

<script setup lang="ts">
import KennerChat from 'components/chat/KennerChat.vue';
import SeasonStandings from 'components/season/SeasonStandings.vue';
import AnnouncementDisplay from 'components/ui/AnnouncementDisplay.vue';
import { useResponsive } from 'src/composables/responsive';
import YearStandings from 'components/YearStandings.vue';
import ContentSection from 'components/base/ContentSection.vue';
import { useQuasar } from 'quasar';
import { ref } from 'vue';
import ScrollContainer from 'components/base/ScrollContainer.vue';

const { isMobile } = useResponsive();
const $q = useQuasar();
const isMdUp = $q.screen.gt.sm;

const mobileContent = ref('chat');
</script>

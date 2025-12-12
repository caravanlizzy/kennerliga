<template>
  <AnnouncementDisplay class="col-auto" />
  <div v-if="isMobile" class="column fit col">
    <q-tab-panels keep-alive class="column col" animated v-model="mobileContent">
      <q-tab-panel name="chat" class="column col">
        <KennerChat class="col"/>
      </q-tab-panel>
      <q-tab-panel name="seasons">
        <SeasonStandings />
      </q-tab-panel>
      <q-tab-panel name="yearly">
        <YearStandings :year="2023" />
      </q-tab-panel>
    </q-tab-panels>
    <q-toolbar class="col-auto bg-primary text-secondary" >
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

const { isMobile } = useResponsive();
const $q = useQuasar();
const isMdUp = $q.screen.gt.sm;

const mobileContent = ref('chat');
</script>

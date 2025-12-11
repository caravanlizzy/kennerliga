<template>
  <AnnouncementDisplay class="col-auto" />
  <div :class="isMobile ? '' : 'q-pa-md'" class="column col">
    <div class="row col">
      <div class="col-12 col-md" :class="{ 'q-pr-md': isMdUp }">
        <ContentSection :isOpened="true" titleEnd :bordered="false" title="Seasons" color="dark">
          <SeasonStandings class="col-12" />
        </ContentSection>
        <ContentSection :bordered="false" titleEnd  title="Year Standings" class="col-12" color="dark">
          <YearStandings :year="2021" />
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

const { isMobile } = useResponsive();
const $q = useQuasar();
const isMdUp = $q.screen.gt.sm;
</script>

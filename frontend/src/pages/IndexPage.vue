<template>
  <div>
    <div :class="isMobile ? 'q-pa-xs' : 'q-pa-md'">
      <AnnouncementDisplay />
      <div class="row">
        <div class="col-12 col-md-8" :class="{ 'q-pr-md': isMdUp }">
          <ContentSection :isOpened="true" title="Seasons" color="primary">
            <SeasonStandings class="col-12" />
          </ContentSection>
          <ContentSection title="Year Standings" class="col-12" color="primary">
            <YearStandings :year="2021" />
          </ContentSection>
        </div>
        <ContentSection
          class="col-12 col-md-4"
          :isOpened="true"
          title="Kennerchat"
          color="primary"
        >
          <KennerChat />
        </ContentSection>
      </div>
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

<template>
  <div>
    <div :class="isMobile ? 'q-pa-xs' : 'q-pa-md'">
      <AnnouncementDisplay />
      <div class="row">
        <div class="col-12 col-md-8" :class="{ 'q-pr-xs': isMdUp }">
          <SeasonStandings class="col-12" />
          <ContentSection
            title="Year Standings"
            class="col-12"
            color="secondary"
          >
            <YearStandings :year="2023" />
          </ContentSection>
        </div>
        <KennerChat class="col-12 col-md-4" />
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

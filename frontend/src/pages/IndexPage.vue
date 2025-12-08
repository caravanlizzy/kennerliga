<template>
  <SideBarLayout side-title="Infos">
    <div :class="isMobile ? 'q-pa-xs' : 'q-pa-md'">
      <AnnouncementDisplay />
      <div class="row q-py-xs" >
        <KennerChat class="col-12" />
        <SeasonStandings class="col-12" />
      </div>
    </div>
    <template #side>
      <FeaturesList />
    </template>
  </SideBarLayout>
</template>

<script setup lang="ts">
import KennerChat from 'components/chat/KennerChat.vue';
import SideBarLayout from 'layouts/SideBarLayout.vue';
import FeaturesList from 'components/dev/FeaturesList.vue';
import SeasonStandings from 'components/season/SeasonStandings.vue';
import AnnouncementDisplay from 'components/ui/AnnouncementDisplay.vue';
import { useResponsive } from 'src/composables/reponsive';

const { isMobile } = useResponsive();
</script>

<template>
  <SideBarLayout side-title="Infos">
    <div :class="isMobile ? 'q-pa-xs' : 'q-pa-md'">
      <AnnouncementDisplay />
      <div class="row q-py-xs">
        <SplitLayout>
          <template #left>
            <KennerChat />
          </template>
          <template #right>
          <SideAccentBox>
            <q-card class="column">
              This will display the yearly standings
            </q-card>
          </SideAccentBox>
          </template>
        </SplitLayout>
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
import { useResponsive } from 'src/composables/responsive';
import SplitLayout from 'layouts/SplitLayout.vue';
import SideAccentBox from 'components/base/SideAccentBox.vue';

const { isMobile } = useResponsive();
</script>

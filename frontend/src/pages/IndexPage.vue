<template>
  <SideBarLayout side-title="Infos">
    <AnnouncementDisplay />
    <div class="row q-px-md q-py-xs">
      <KennerChat class="col-12" />
      <SeasonStandings class="col-12" />
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
</script>

<template>
  <SideBarLayout side-title="Infos">
    <div class="row">
      <CurrentSeason v-if="seasonId" :seasonId="seasonId" class="col-12" />
      <SeasonStandings class="col-12" />
      <KennerChat class="col-12" />
    </div>
    <template #side>
      <FeaturesList />
      <YearStandings />
    </template>
  </SideBarLayout>
</template>

<script setup lang="ts">
import KennerChat from 'components/chat/KennerChat.vue';
import YearStandings from 'components/league/YearStandings.vue';
import CurrentSeason from 'components/season/CurrentSeason.vue';
import SideBarLayout from 'layouts/SideBarLayout.vue';
import FeaturesList from 'components/dev/FeaturesList.vue';
import SeasonStandings from 'components/season/SeasonStandings.vue';

</script>

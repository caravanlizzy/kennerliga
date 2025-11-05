<template>
  <SideBarLayout side-title="Infos">
    <div class="row">
      <CurrentSeason v-if="seasonId" :seasonId="seasonId" class="col-12" />
      <PastSeaons class="col-12" />
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
import { onMounted, ref } from 'vue';
import { useLeagueStore } from 'stores/leagueStore';
import SideBarLayout from 'layouts/SideBarLayout.vue';
import { fetchCurrentSeasonId } from 'src/services/seasonService';
import PastSeaons from 'components/season/PastSeaons.vue';
import FeaturesList from 'components/dev/FeaturesList.vue';
import { getMyLeagueId } from 'src/services/leagueService';

const { init } = useLeagueStore();

const seasonId = ref<number | null>(null);

onMounted(async () => {
  seasonId.value = await fetchCurrentSeasonId() || null;
  const leagueId = await getMyLeagueId();
  if (leagueId !== null) {
    void init();
  }
});
</script>

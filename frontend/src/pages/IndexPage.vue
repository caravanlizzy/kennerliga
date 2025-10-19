<template>
  <SideBarLayout side-title="Year Standings">
    <div class="q-px-lg q-py-lg row">
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
import { getMyLeagueId } from 'src/services/game/leagueService';
import SideBarLayout from 'layouts/SideBarLayout.vue';
import { getCurrentSeasonId } from 'src/services/seasonService';
import PastSeaons from 'components/season/PastSeaons.vue';
import FeaturesList from 'components/dev/FeaturesList.vue';

const { init } = useLeagueStore();

const seasonId = ref<number | null>(null);

onMounted(async () => {
  seasonId.value = await getCurrentSeasonId() || null;
  const leagueId = await getMyLeagueId();
  if (leagueId !== null) {
    void init();
  }
});
</script>

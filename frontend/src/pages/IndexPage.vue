<template>
  <SideBarLayout side-title="Year Standings">
    <div class="q-pl-lg q-py-lg row">
      <CurrentSeason class="col-12"/>
      <SeasonList class="col-12"/>
      <KennerChat class="col-9" />
    </div>
    <template #side>
      <YearStandings />
    </template>
  </SideBarLayout>

</template>

<script setup lang="ts">
import KennerChat from 'components/chat/KennerChat.vue';
import YearStandings from 'components/league/YearStandings.vue';
import CurrentSeason from 'components/season/CurrentSeason.vue';
import SeasonList from 'components/season/SeasonList.vue';
import { onMounted } from 'vue';
import { useLeagueStore } from 'stores/leagueStore';
import { getMyLeagueId } from 'src/services/game/leagueService';
import SideBarLayout from 'layouts/SideBarLayout.vue';

const { init } = useLeagueStore();

onMounted(async() => {
  const leagueId = await getMyLeagueId();
  if (leagueId !== null) {
    void init();
  }
});
</script>

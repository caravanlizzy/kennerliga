<template>
  <SideBarLayout side-title="Year Standings">
    <div class="q-pl-lg q-py-lg row">
      <CurrentSeason :seasonId="seasonId" class="col-12" />
      <SeasonList class="col-12" />
      <KennerChat class="col-12" />
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
import { onMounted, ref } from 'vue';
import { useLeagueStore } from 'stores/leagueStore';
import { getMyLeagueId } from 'src/services/game/leagueService';
import SideBarLayout from 'layouts/SideBarLayout.vue';
import { getCurrentSeasonId } from 'src/services/seasonService';

const { init } = useLeagueStore();

const seasonId = ref<number | null>(null);

onMounted(async () => {
  seasonId.value = await getCurrentSeasonId();
  const leagueId = await getMyLeagueId();
  if (leagueId !== null) {
    void init();
  }
});
</script>

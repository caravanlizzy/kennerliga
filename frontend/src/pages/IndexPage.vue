<template>
  <q-page :class="{ 'row items-start': !isMobile }">
    <CurrentSeason/>
    <SeasonList />
    <KennerChat class="col-9" />
    <YearStandings class="col-3" />
  </q-page>
</template>

<script setup lang="ts">
import { useResponsive } from 'src/composables/reponsive';
import KennerChat from 'components/chat/KennerChat.vue';
import YearStandings from 'components/league/YearStandings.vue';
import CurrentSeason from 'components/season/CurrentSeason.vue';
import SeasonList from 'components/season/SeasonList.vue';

const { isMobile } = useResponsive();
</script>

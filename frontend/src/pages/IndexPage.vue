<template>
  <q-page :class="{ 'row items-start': !isMobile }">
    <KennerChat class="col-9" />
    <YearStandings class="col-3" />
  </q-page>
</template>

<script setup lang="ts">
import { useResponsive } from 'src/composables/reponsive';
import KennerChat from 'components/chat/KennerChat.vue';
import YearStandings from 'components/league/YearStandings.vue';

const { isMobile } = useResponsive();
</script>

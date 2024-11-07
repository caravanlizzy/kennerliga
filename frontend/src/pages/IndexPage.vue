<template>
  <q-page :class="{'row items-start': !isMobile}">
    <TheWelcomeBox class="col-12" />
      <KennerChat class="col-9" />
    <YearStandings class="col-3" />
  </q-page>
</template>

<script setup lang="ts">

import { useResponsive } from 'src/composables/reponsive';
import KennerChat from 'components/chats/KennerChat.vue';
import TheWelcomeBox from 'components/singles/TheWelcomeBox.vue';
import YearStandings from 'components/singles/YearStandings.vue';

const { isMobile } = useResponsive();

</script>

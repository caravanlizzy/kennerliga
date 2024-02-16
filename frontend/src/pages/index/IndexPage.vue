<template>
  <q-page :class="{'q-pa-lg': !isMobile}">
    <the-welcome-box class=""/>
    <kenner-chat class="" />
  </q-page>
</template>

<script setup lang="ts">

import { useResponsive } from 'src/composables/reponsive';
import { useUserStore } from 'stores/userStore';
import KennerChat from 'components/chats/KennerChat.vue';
import TheWelcomeBox from 'components/TheWelcomeBox.vue';

const { isMobile } = useResponsive();
const store = useUserStore();

</script>

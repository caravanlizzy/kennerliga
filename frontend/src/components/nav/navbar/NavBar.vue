<template>
  <q-toolbar-title class="row no-wrap items-center justify-between">
    <nav-top-left />
    <nav-top-center />
    <nav-top-right />
  </q-toolbar-title>
</template>
<script setup lang="ts">

import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import NavTopLeft from 'components/nav/navbar/NavTopLeft.vue';
import NavTopCenter from 'components/nav/navbar/NavTopCenter.vue';
import NavTopRight from 'components/nav/navbar/NavTopRight.vue';

const userStore = useUserStore();
const { loggedIn } = storeToRefs(userStore);
</script>

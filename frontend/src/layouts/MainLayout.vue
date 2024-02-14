<template>
  <q-layout class="column" view="hHh Lpr lFf">
    <q-header bordered elevated >
      <q-toolbar class="bg-white ">
        <nav-bar />
      </q-toolbar>
    </q-header>

    <q-page-container class="flex column justify-center">
      <BreadCrumbs v-if="loggedIn" />
      <router-view class="text-primary q-pa-lg" />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import BreadCrumbs from 'components/nav/BreadCrumbs.vue';
import NavBar from 'components/nav/navbar/NavBar.vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';

const store = useUserStore();
const { loggedIn } = storeToRefs(store);
</script>

<style scoped>
</style>

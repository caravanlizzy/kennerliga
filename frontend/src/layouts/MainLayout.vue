<template>
  <q-layout class="bg-primary column" view="hHh Lpr lFf">
    <q-header elevated>
      <q-toolbar class="bg-primary">
        <nav-bar />
      </q-toolbar>
    </q-header>

    <q-page-container class="flex column justify-center">
      <BreadCrumbs />
      <router-view class="text-white" />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import BreadCrumbs from 'components/nav/BreadCrumbs.vue';
import NavBar from 'components/nav/navbar/NavBar.vue';
</script>

<style scoped>
</style>

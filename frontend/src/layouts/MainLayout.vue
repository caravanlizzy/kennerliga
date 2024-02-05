<template>
  <q-layout class="bg-primary column" view="hHh Lpr lFf">
    <q-header elevated>
      <q-toolbar class="bg-primary row justify-between">
        <NavTopLeft class="col-3" />
        <NavTopCenter class="col-8" />
        <NavTopRight class="col" />
      </q-toolbar>
    </q-header>

    <q-page-container  class="flex column justify-center">
      <BreadCrumbs  />
      <router-view class="q-pa-lg full-height text-white " />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import BreadCrumbs from 'components/nav/BreadCrumbs.vue';
import NavTopCenter from 'components/nav/NavTopCenter.vue';
import NavTopRight from 'components/nav/NavTopRight.vue';
import NavTopLeft from 'components/nav/NavTopLeft.vue';

</script>

<style scoped>
</style>

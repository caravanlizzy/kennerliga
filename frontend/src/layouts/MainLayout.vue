<template>
  <q-layout class="bg-primary" view="hHh Lpr lFf">
    <q-header elevated>
      <q-toolbar class="bg-primary row justify-between items-center q-py-xs">

        <q-toolbar-title shrink class="text-secondary">
          <div class="row items-center ">
            <q-btn :to="{ name: 'home' }" flat class="q-mr-md" size="xl" outlined icon="pets" />
            <span class="text-bold text-h4" >Kennerliga</span>
          </div>
        </q-toolbar-title>

        <ToolbarTop />
        <div class="row">
          <q-btn stretch size="xl" flat icon="settings"></q-btn>
          <q-btn stretch size="lg" flat icon="logout" color="negative" />
        </div>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <BreadCrumbs />
      <router-view class="q-pa-lg text-white" />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import ToolbarTop from 'components/nav/ToolbarTop.vue';
import BreadCrumbs from 'components/nav/BreadCrumbs.vue';

</script>

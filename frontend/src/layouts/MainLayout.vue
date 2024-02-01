<template>
  <q-layout class="bg-primary" view="hHh Lpr lFf">
    <q-header elevated>
      <q-toolbar class="bg-primary row justify-between items-center q-py-xs">

        <q-toolbar-title shrink class="text-secondary">
          <div class="row items-center" >
            <q-btn flat outline class="q-mx-sm" size="xl" outlined icon="pets" />
            <span class="text-italic text-h4">Kennerliga</span>
          </div>
        </q-toolbar-title>

        <ToolbarTop />
        <div>
          <q-btn size="xl" flat icon="settings"></q-btn>
          <q-btn size="lg" flat icon="logout" color="negative" />
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

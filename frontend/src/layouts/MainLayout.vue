<template>
  <q-layout class="bg-primary" view="hHh Lpr lFf">
    <q-header elevated>
      <q-toolbar class="bg-primary">

        <q-toolbar-title class="text-secondary">
          Kennerliga
        </q-toolbar-title>

        <ToolbarTop />
        <q-btn flat dense round icon="menu" aria-label="Menu" class="text-info" @click="toggleDrawer" />
      </q-toolbar>
    </q-header>

    <AdminSidebar :drawer-open="drawerOpen"/>

    <q-page-container>
      <NavbarTop />
      <q-separator color="info" />
      <router-view class="q-pa-lg" />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import ToolbarTop from 'components/nav/ToolbarTop.vue';
import NavbarTop from 'components/nav/NavbarTop.vue';
import AdminSidebar from 'components/nav/AdminSidebar.vue';
import { ref } from 'vue';

const drawerOpen = ref(false)
const toggleDrawer = () => {
  drawerOpen.value = !drawerOpen.value
}
</script>

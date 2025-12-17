<template>
  <q-layout class="column" view="hHh Lpr lFf">
    <q-header bordered class="text-dark bg-white col-auto">
      <NavBar :onToggle="toggleDrawer" />
    </q-header>

    <KennerDrawer v-model="drawerState" />

    <q-page-container class="col column">
      <div
        class="q-mx-auto"
        style="max-width: 1300px; width: 100%; "
      >
        <router-view />
        <ConfirmDialog />
      </div>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import NavBar from 'components/layout/NavBar.vue';
import { ref, Ref } from 'vue';
import KennerDrawer from 'components/layout/KennerDrawer.vue';
import ConfirmDialog from 'components/ui/ConfirmDialog.vue';

const drawerState: Ref<boolean> = ref(false);

function toggleDrawer(): void {
  drawerState.value = !drawerState.value;
}
</script>

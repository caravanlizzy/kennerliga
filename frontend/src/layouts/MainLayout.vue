<template>
  <q-layout class="column" view="hHh Lpr lFf">
    <q-header bordered elevated>
      <q-toolbar class="bg-white ">
        <nav-bar :onToggle="toggleDrawer" />
      </q-toolbar>
    </q-header>

    <KennerDrawer v-model="drawerState"/>

    <q-page-container class="flex column justify-center">
      <BreadCrumbs v-if="loggedIn" />
      <router-view class="text-primary q-pa-lg" />
    </q-page-container>

  </q-layout>
</template>

<script setup lang="ts">
import BreadCrumbs from 'components/nav/BreadCrumbs.vue';
import NavBar from 'components/nav/NavBar.vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import KennerDrawer from 'components/KennerDrawer.vue';
import { ref, Ref } from 'vue';

const store = useUserStore();
const { loggedIn } = storeToRefs(store);
const drawerState:Ref<boolean> = ref(true);
function toggleDrawer():void {
  drawerState.value = !drawerState.value;
}

</script>

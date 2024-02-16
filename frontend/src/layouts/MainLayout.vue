<template>
  <q-layout class="column" view="hHh Lpr lFf">
    <q-header bordered >
      <q-toolbar  class="bg-white ">
        <nav-bar :onToggle="toggleDrawer" />
      </q-toolbar>
    </q-header>

    <KennerDrawer v-model="drawerState"/>

    <q-page-container class="flex column justify-center ">
      <BreadCrumbs v-if="loggedIn" />
      <div :class="{'q-pa-lg': !isMobile}">
        <router-view class=" text-primary" />
      </div>
    </q-page-container>

  </q-layout>
</template>

<script setup lang="ts">
import BreadCrumbs from 'components/nav/BreadCrumbs.vue';
import NavBar from 'components/nav/NavBar.vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import KennerDrawer from 'components/drawer/KennerDrawer.vue';
import { ref, Ref } from 'vue';
import { useResponsive } from 'src/composables/reponsive';

const store = useUserStore();
const { isMobile } = useResponsive();
const { loggedIn } = storeToRefs(store);
const drawerState:Ref<boolean> = ref(false);
function toggleDrawer():void {
  drawerState.value = !drawerState.value;
}

</script>

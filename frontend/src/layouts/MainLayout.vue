<template>
  <q-layout class="column" view="hHh Lpr lFf">
    <q-header>
      <q-toolbar class="background-navbar">
        <NavBar :onToggle="toggleDrawer" />
      </q-toolbar>
<!--      <BreadCrumbs v-if="isAuthenticated" />-->
      <Announcements v-if="announcements.length > 0" />
    </q-header>

    <KennerDrawer v-model="drawerState" />

    <q-page-container class="flex column justify-center">
      <div :class="{ 'q-pa-lg': !isMobile }">
        <router-view class="text-primary" />
      </div>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import NavBar from 'components/layout/NavBar.vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import { ref, Ref } from 'vue';
import { useResponsive } from 'src/composables/reponsive';
import Announcements from 'components/announcement/AnnouncementList.vue';
import DevTools from 'components/DevTools.vue';
import { useAnnouncementStore } from 'stores/announcementStore';
import KennerDrawer from 'components/layout/KennerDrawer.vue';

const store = useUserStore();
const { announcements } = useAnnouncementStore();
const { isMobile } = useResponsive();
const { isDev } = storeToRefs(store);
const drawerState: Ref<boolean> = ref(false);

function toggleDrawer(): void {
  drawerState.value = !drawerState.value;
}
</script>

<style scoped lang="scss">
.background-navbar {
  background-color: #4d4949;
}
</style>

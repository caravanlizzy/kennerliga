<template>
  <q-layout class="column" view="hHh Lpr lFf">
    <q-header>
      <q-toolbar class="background-navbar">
        <NavBar :onToggle="toggleDrawer" />
      </q-toolbar>
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
import { ref, Ref } from 'vue';
import { useResponsive } from 'src/composables/reponsive';
import Announcements from 'components/announcement/AnnouncementList.vue';
import { useAnnouncementStore } from 'stores/announcementStore';
import KennerDrawer from 'components/layout/KennerDrawer.vue';

const { announcements } = useAnnouncementStore();
const { isMobile } = useResponsive();
const drawerState: Ref<boolean> = ref(false);

function toggleDrawer(): void {
  drawerState.value = !drawerState.value;
}
</script>

<style scoped lang="scss">
.background-navbar {
  background-color: #ffffff;
  border-bottom: 1px solid #b15f3a;
}
</style>

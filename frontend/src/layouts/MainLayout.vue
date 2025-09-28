<template>
  <q-layout class="column" view="hHh Lpr lFf">
    <q-header bordered class="bg-transparent text-primary">
      <NavBar :onToggle="toggleDrawer" />
      <DevTools v-show="isDev" />
      <Announcements v-if="announcements.length > 0" />
    </q-header>

    <KennerDrawer v-model="drawerState" />

    <q-page-container class="flex column justify-center q-pa-md">
      <div :class="{ '': !isMobile }">
        <router-view class="text-primary" />
      </div>
      <ConfirmDialog />
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
import ConfirmDialog from 'components/ui/ConfirmDialog.vue';
import { useUiStore } from 'stores/uiStore';
import { storeToRefs } from 'pinia';
import DevTools from 'components/ui/DevTools.vue';

const { announcements } = useAnnouncementStore();
const { isMobile } = useResponsive();
const { isDev } = storeToRefs(useUiStore());
const drawerState: Ref<boolean> = ref(false);

function toggleDrawer(): void {
  drawerState.value = !drawerState.value;
}
</script>

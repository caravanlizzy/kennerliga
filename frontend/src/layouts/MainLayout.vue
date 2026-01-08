<template>
  <q-layout class="column" view="hHh Lpr lFf">
    <q-header class="col-auto no-shadow bg-transparent">
      <NavBar :onToggle="toggleDrawer" />
    </q-header>

    <KennerDrawer v-model="drawerState" />
    <q-drawer
      v-if="isAuthenticated"
      side="left"
      v-model="chatDrawerOpen"
      :width="380"
      :behavior="isMobile ? 'mobile' : 'desktop'"
      :overlay="isMobile"
      class="chat-drawer glass-drawer"
    >
      <div class="column full-height">
        <div class="q-pa-md row items-center justify-between border-bottom-subtle bg-white">
          <div class="row items-center">
            <q-icon name="chat" color="blue-grey-8" size="sm" class="q-mr-sm" />
            <div class="text-h6 text-weight-bold">Kennerchat</div>
          </div>
          <q-btn flat round dense icon="close" size="sm" color="grey-7" @click="chatDrawerOpen = false">
            <q-tooltip>Minimize Chat</q-tooltip>
          </q-btn>
        </div>
        <KennerChat class="col bg-white" />
      </div>
    </q-drawer>

    <!-- Chat Toggle Button (Left) -->
    <div
      v-if="isAuthenticated && !chatDrawerOpen && !isMobile"
      class="fixed-bottom-left q-ma-md"
      style="z-index: 2000"
    >
      <q-btn
        round
        size="lg"
        color="blue-grey-8"
        icon="chat"
        class="shadow-10 glass-toggle"
        @click="chatDrawerOpen = true"
      >
      </q-btn>
    </div>

    <q-page-container class="col column bg-white">
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
import { ref, Ref, onMounted } from 'vue';
import KennerDrawer from 'components/layout/KennerDrawer.vue';
import ConfirmDialog from 'components/ui/ConfirmDialog.vue';
import KennerChat from 'components/chat/KennerChat.vue';
import { useUserStore } from 'stores/userStore';
import { useResponsive } from 'src/composables/responsive';
import { storeToRefs } from 'pinia';

const drawerState: Ref<boolean> = ref(false);
const { isAuthenticated } = storeToRefs(useUserStore());
const { isMobile } = useResponsive();

const chatDrawerOpen = ref(false);

onMounted(() => {
  chatDrawerOpen.value = isAuthenticated.value && !isMobile;
});

function toggleDrawer(): void {
  drawerState.value = !drawerState.value;
}
</script>

<style lang="scss">
.border-bottom {
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}
.border-bottom-subtle {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}
.chat-drawer {
  border-right: 1px solid rgba(0, 0, 0, 0.05) !important;
}
.glass-drawer {
  background: rgba(255, 255, 255, 0.4) !important;
  backdrop-filter: blur(12px);
  border-right: 1px solid rgba(54, 64, 88, 0.1) !important;
}
.glass-toggle {
  background: rgba(255, 255, 255, 0.7) !important;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(54, 64, 88, 0.1);
  color: #455a64 !important; // blue-grey-8
}
</style>

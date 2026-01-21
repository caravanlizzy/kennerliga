<template>
  <q-layout class="column" view="hHh LpR lFf">
    <q-header class="col-auto no-shadow bg-transparent">
      <NavBar :onToggle="toggleDrawer" />
    </q-header>

    <q-drawer
      side="right"
      v-model="drawerState"
      :width="300"
      :behavior="isMobile ? 'mobile' : 'desktop'"
      :overlay="true"
      class="kenner-drawer"
    >
      <KennerDrawer v-model="drawerState" />
    </q-drawer>

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
            <q-icon name="chat" color="primary" size="sm" class="q-mr-sm" />
          </div>
          <q-btn flat round dense icon="chevron_left" size="sm" color="primary" @click="toggleChat">
            <q-tooltip>Hide Chat</q-tooltip>
          </q-btn>
        </div>
        <KennerChat class="col bg-white" />
      </div>
    </q-drawer>

    <div
      v-if="isAuthenticated"
      class="fixed-left z-max"
      style="top: 66px;"
    >
      <q-btn
        v-if="!chatDrawerOpen && !isMobile"
        flat
        dense
        color="primary"
        class="chat-mini-toggle glass-toggle"
        @click="toggleChat"
      >
        <div class="column items-center q-py-sm">
          <q-icon name="chat" size="xs" />
          <div class="vertical-text text-weight-bold q-mt-xs">CHAT</div>
          <q-icon name="chevron_right" size="xs" class="q-mt-xs" />
        </div>
        <q-tooltip anchor="center right" self="center left">Show Chat</q-tooltip>
      </q-btn>
    </div>

    <q-page-container class="col column bg-white">
      <div
        class="q-mx-auto"
        style="max-width: 1300px; width: 100%; "
      >
        <router-view v-slot="{ Component }">
          <component :is="Component" />
        </router-view>
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
import { useUiStore } from 'stores/uiStore';
import { useResponsive } from 'src/composables/responsive';
import { storeToRefs } from 'pinia';

const drawerState: Ref<boolean> = ref(false);
const { isAuthenticated } = storeToRefs(useUserStore());
const uiStore = useUiStore();
const { isMobile } = useResponsive();
const { chatDrawerOpen } = storeToRefs(uiStore);
const { toggleChat } = uiStore;

onMounted(() => {
  chatDrawerOpen.value = isAuthenticated.value && !isMobile.value;
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
  border-right: 2px solid #eeeeee !important;
}
.glass-drawer {
  background: rgba(255, 255, 255, 0.4) !important;
  backdrop-filter: blur(12px);
}
.glass-toggle {
  background: rgba(255, 255, 255, 0.7) !important;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(0, 0, 0, 0.05);
  color: $primary !important;
}

.chat-mini-toggle {
  border-radius: 0 0 12px 0 !important;
  border-left: none !important;
  border-top: none !important;
  box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;

  &:hover {
    padding-left: 8px;
    background: rgba(255, 255, 255, 0.9) !important;
  }
}

.vertical-text {
  writing-mode: vertical-rl;
  text-orientation: mixed;
  letter-spacing: 2px;
  font-size: 10px;
}
</style>

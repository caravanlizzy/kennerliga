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
      class="kenner-drawer"
    >
      <KennerDrawer v-model="drawerState" />
    </q-drawer>

    <q-drawer
      v-if="isAuthenticated"
      side="left"
      v-model="chatDrawerOpen"
      :width="320"
      :behavior="isMobile ? 'mobile' : 'desktop'"
      class="chat-drawer"
    >
      <div class="column full-height">
        <div class="q-pa-md row items-center justify-between border-bottom-subtle bg-white">
          <div class="row items-center">
            <q-icon name="chat" color="teal" size="sm" class="q-mr-sm" />
          </div>
          <q-btn flat round dense icon="chevron_left" size="sm" color="teal" @click="toggleChat">
            <q-tooltip>Hide Chat</q-tooltip>
          </q-btn>
        </div>
        <KennerChat class="col bg-white" />
      </div>
    </q-drawer>

    <div
      v-if="isAuthenticated"
      class="fixed-left z-max"
      style="top: 100px;"
    >
      <q-btn
        v-if="!chatDrawerOpen && !isMobile"
        flat
        dense
        color="teal"
        class="chat-mini-toggle"
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

    <MobileBottomNav />
  </q-layout>
</template>

<script setup lang="ts">
import MobileBottomNav from 'components/layout/MobileBottomNav.vue';
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
  chatDrawerOpen.value = false;
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
.kenner-drawer {
  border-left: 1px solid rgba(0, 0, 0, 0.05) !important;
}

.chat-mini-toggle {
  border-radius: 0 12px 12px 0 !important;
  border-left: none !important;
  box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;

  &:hover {
    padding-left: 12px;
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

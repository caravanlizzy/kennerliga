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
      :width="350"
      :behavior="isMobile ? 'mobile' : 'desktop'"
      class="chat-drawer glass-effect shadow-10"
    >
      <div class="column full-height kenner-drawer-container">
        <div class="q-pa-lg q-mb-sm row items-center border-bottom-subtle bg-white/50">
          <div class="row items-center">
            <q-icon name="chat" color="teal" size="32px" class="q-mr-sm" />
            <span class="text-h5 text-weight-bolder tracking-tighter" style="letter-spacing: -1px;">
              <span class="text-teal">Kenner</span><span class="text-grey-9">Chat</span>
            </span>
          </div>
          <q-space />
          <q-btn flat round dense icon="close" color="grey-7" class="hover-scale" @click="toggleChat">
            <q-tooltip>Close Chat</q-tooltip>
          </q-btn>
        </div>
        <KennerChat class="col bg-transparent" />
      </div>
    </q-drawer>

    <!-- Removed fixed chat toggle -->

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
  border-right: 1px solid rgba(0, 0, 0, 0.08) !important;
  box-shadow: 10px 0 30px rgba(0, 0, 0, 0.05);
}
.kenner-drawer {
  border-left: 1px solid rgba(0, 0, 0, 0.08) !important;
  box-shadow: -10px 0 30px rgba(0, 0, 0, 0.05);
}

// Removed unused styles: .chat-mini-toggle, .vertical-text
</style>

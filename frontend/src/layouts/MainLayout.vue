<template>
  <q-layout class="column" view="hHh Lpr lFf">
    <q-header class="col-auto no-shadow bg-transparent">
      <NavBar :onToggle="toggleDrawer" />
    </q-header>

    <KennerDrawer v-model="drawerState" />
    <q-drawer
      v-if="isAuthenticated && !isMobile"
      side="left"
      v-model="chatDrawerOpen"
      :width="380"
      bordered
      class="bg-white chat-drawer"
    >
      <div class="column full-height">
        <div class="q-pa-md row items-center justify-between border-bottom-subtle">
          <div class="row items-center">
            <q-icon name="chat" color="primary" size="sm" class="q-mr-sm" />
            <div class="text-h6 text-weight-bold">Kennerchat</div>
          </div>
          <q-btn flat round dense icon="close" size="sm" color="grey-7" @click="chatDrawerOpen = false">
            <q-tooltip>Minimize Chat</q-tooltip>
          </q-btn>
        </div>
        <KennerChat class="col" />
      </div>
    </q-drawer>

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
import { ref, Ref, computed } from 'vue';
import KennerDrawer from 'components/layout/KennerDrawer.vue';
import ConfirmDialog from 'components/ui/ConfirmDialog.vue';
import KennerChat from 'components/chat/KennerChat.vue';
import { useUserStore } from 'stores/userStore';
import { useResponsive } from 'src/composables/responsive';
import { useUiStore } from 'src/stores/uiStore';
import { storeToRefs } from 'pinia';

const drawerState: Ref<boolean> = ref(false);
const { isAuthenticated } = storeToRefs(useUserStore());
const { isMobile } = useResponsive();
const uiStore = useUiStore();

const chatDrawerOpen = computed({
  get: () => isAuthenticated.value && !isMobile && !uiStore.isMinimized('kennerchat'),
  set: (val) => {
    if (!val) {
      uiStore.minimize({
        id: 'kennerchat',
        title: 'Kennerchat',
        icon: 'chat',
        color: 'primary',
        type: 'section'
      });
    } else {
      uiStore.restore('kennerchat');
    }
  }
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
</style>

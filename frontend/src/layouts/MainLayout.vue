<template>
  <q-layout view="hHh LpR fFf">
    <q-header class="no-shadow bg-transparent">
      <NavBar :onToggle="toggleDrawer" />
      <BreadcrumbBar />
      <AnnouncementDisplay v-if="isMobile && isAuthenticated" no-margins />
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

    <q-page-container class="main-container">
      <div
        class="q-mx-auto"
        :class="isMobile ? 'q-px-none' : 'q-px-md q-pt-md'"
        style="max-width: var(--kenner-max-width); width: 100%"
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
import BreadcrumbBar from 'components/layout/BreadcrumbBar.vue';
import NavBar from 'components/layout/NavBar.vue';
import { ref, Ref } from 'vue';
import KennerDrawer from 'components/layout/KennerDrawer.vue';
import ConfirmDialog from 'components/ui/ConfirmDialog.vue';
import AnnouncementDisplay from 'components/ui/AnnouncementDisplay.vue';
import { useUserStore } from 'stores/userStore';
import { useResponsive } from 'src/composables/responsive';
import { storeToRefs } from 'pinia';

const drawerState: Ref<boolean> = ref(false);
const { isAuthenticated } = storeToRefs(useUserStore());
const { isMobile } = useResponsive();

function toggleDrawer(): void {
  drawerState.value = !drawerState.value;
}
</script>

<style lang="scss">
.main-container {
}

.border-bottom {
  border-bottom: 1px solid var(--kenner-border-color);
}
.border-bottom-subtle {
  border-bottom: 1px solid rgba(0, 0, 0, 0.03);

  .body--dark & {
    border-bottom-color: var(--kenner-border-subtle);
  }
}
.kenner-drawer {
  border-left: 1px solid var(--kenner-border-color) !important;
}
</style>

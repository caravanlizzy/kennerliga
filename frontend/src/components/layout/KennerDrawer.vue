<template>
  <div class="column full-height kenner-drawer-container glass-effect">
    <!-- Drawer Header -->
    <div class="q-pa-md q-mb-sm row items-center border-bottom-subtle">
      <q-icon name="img:icons/favicon.svg" size="32px" class="q-mr-sm" />
      <span class="text-h6 text-weight-bold tracking-tighter" style="letter-spacing: -0.5px;"><span class="text-primary">Kenner</span><span class="text-accent">Liga</span></span>
      <q-space />
      <q-btn flat round dense icon="close" color="grey-7" @click="drawerState = false" />
    </div>

    <!-- Drawer Content -->
    <div class="col scroll">
      <q-list class="q-py-md">
        <DrawerSubGroup>General</DrawerSubGroup>
        <DrawerItem icon="feedback" icon-color="orange-8" label="Feedback" forward-name="feedback" />
        <DrawerItem
          icon="calendar_month"
          icon-color="blue-8"
          label="Seasons"
          forward-name="seasons"
        />
        <DrawerItem icon="group" icon-color="teal-7" label="Members" forward-name="users" />
        <DrawerItem icon="gavel" icon-color="primary" label="Rules" forward-name="rules" />

        <template v-if="isAdmin">
          <q-separator class="q-my-sm drawer-separator" />
          <DrawerSubGroup>Management</DrawerSubGroup>
          <DrawerItem icon="casino" icon-color="indigo-7" label="Games" forward-name="games" />
          <DrawerItem
            icon="forward_to_inbox"
            icon-color="deep-purple-7"
            label="Invitations"
            forward-name="invitations"
          />
        </template>

        <template v-if="isAdmin">
          <q-separator class="q-my-sm drawer-separator" />
          <DrawerSubGroup>Development</DrawerSubGroup>
          <DrawerItem icon="terminal" icon-color="grey-9" label="Hijack (Dev)" forward-name="dev" />
        </template>
      </q-list>
    </div>

    <div class="q-pb-lg">
      <DrawerItem icon="logout" icon-color="red-7" label="Logout" @click="doLogout" />
    </div>
  </div>
</template>

<script setup lang="ts">
import DrawerItem from 'components/base/DrawerItem.vue';
import DrawerSubGroup from 'components/base/DrawerSubGroup.vue';
import { useUserStore } from 'stores/userStore';
import { useResponsive } from 'src/composables/responsive';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';
import { provide } from 'vue';

const drawerState = defineModel();

const responsive = useResponsive();
const { logout } = useUserStore();
const { isAdmin } = storeToRefs(useUserStore());

const router = useRouter();

provide('closeDrawer', () => (drawerState.value = false));

async function doLogout(): Promise<void> {
  await logout();
  drawerState.value = false;
  await router.push({ name: 'home' });
}
</script>

<style lang="scss">
.kenner-drawer-container {
  background: rgba(255, 255, 255, 0.9) !important;
}

.glass-effect {
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

.border-bottom-subtle {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.drawer-separator {
  opacity: 0.3;
  margin: 12px 16px;
}

.kenner-drawer {
  border-left: 2px solid #cfd8dc !important;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.02);
}
</style>

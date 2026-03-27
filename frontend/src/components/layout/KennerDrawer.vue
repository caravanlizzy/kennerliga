<template>
  <div class="column full-height kenner-drawer-container glass-effect">
    <!-- Drawer Header -->
    <div class="q-pa-lg q-mb-sm row items-center border-bottom-subtle bg-white/50">
      <q-icon name="img:icons/favicon.svg" size="36px" class="q-mr-sm" />
      <span class="text-h5 text-weight-bolder tracking-tighter" style="letter-spacing: -1px;">
        <span class="text-primary">Kenner</span><span class="text-accent">Liga</span>
      </span>
      <q-space />
      <q-btn flat round dense icon="close" color="grey-7" class="hover-scale" @click="drawerState = false" />
    </div>

    <!-- Drawer Content -->
    <div class="col scroll q-px-sm">
      <q-list class="q-py-sm">
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

    <div class="q-pa-md q-pb-xl">
      <q-separator class="q-mb-md drawer-separator" />
      <DrawerItem icon="logout" icon-color="red-7" label="Logout" class="logout-item" @click="doLogout" />
    </div>
  </div>
</template>

<script setup lang="ts">
import DrawerItem from 'components/base/DrawerItem.vue';
import DrawerSubGroup from 'components/base/DrawerSubGroup.vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';
import { provide } from 'vue';

const drawerState = defineModel();

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
  background: rgba(255, 255, 255, 0.85) !important;
}

.glass-effect {
  backdrop-filter: blur(25px) saturate(180%);
  -webkit-backdrop-filter: blur(25px) saturate(180%);
}

.border-bottom-subtle {
  border-bottom: 1px solid rgba(0, 0, 0, 0.03);
}

.drawer-separator {
  opacity: 0.15;
  margin: 16px 24px;
}

.logout-item {
  border: 1px solid rgba(255, 0, 0, 0.05);
  background: rgba(255, 0, 0, 0.02);
  &:hover {
    background: rgba(255, 0, 0, 0.06);
    color: #d32f2f !important;
  }
}

.hover-scale {
  transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  &:hover {
    transform: scale(1.1);
  }
}

.kenner-drawer {
}
</style>

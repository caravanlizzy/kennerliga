<template>
  <div class="column full-height kenner-drawer-container glass-effect">
    <!-- Drawer Header -->
    <div class="q-pa-lg q-mb-sm row items-center border-bottom-subtle bg-drawer-header">
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
        <DrawerItem
          icon="task_alt"
          icon-color="green-7"
          label="Task Board"
          forward-name="taskboard"
        />

        <q-separator class="q-my-sm drawer-separator" />
        <DrawerSubGroup>Appearance</DrawerSubGroup>
        <q-item class="drawer-item q-mx-sm q-my-xs squircle-shape">
          <q-item-section avatar class="drawer-item__icon-section">
            <q-icon
              :name="$q.dark.isActive ? 'dark_mode' : 'light_mode'"
              size="22px"
              :color="$q.dark.isActive ? 'amber' : 'grey-7'"
            />
          </q-item-section>
          <q-item-section class="drawer-item__text-section">
            <q-item-label class="text-subtitle2 text-weight-medium">
              Dark Mode
            </q-item-label>
          </q-item-section>
          <q-item-section side>
            <q-toggle
              :model-value="$q.dark.isActive"
              @update:model-value="toggleDarkMode"
              color="primary"
            />
          </q-item-section>
        </q-item>

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
import { useQuasar } from 'quasar';

const drawerState = defineModel();

const { logout } = useUserStore();
const { isAdmin } = storeToRefs(useUserStore());

const router = useRouter();
const $q = useQuasar();

provide('closeDrawer', () => (drawerState.value = false));

function toggleDarkMode(val: boolean): void {
  $q.dark.set(val);
}

async function doLogout(): Promise<void> {
  await logout();
  drawerState.value = false;
  await router.push({ name: 'home' });
}
</script>

<style lang="scss">
.kenner-drawer-container {
}

.body--dark .kenner-drawer-container {
}

.body--dark .border-bottom-subtle {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
}

.bg-drawer-header {
}

.body--dark .bg-drawer-header {
}

.glass-effect {
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
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

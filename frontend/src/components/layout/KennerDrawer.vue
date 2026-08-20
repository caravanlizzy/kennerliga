<template>
  <div class="column full-height kenner-drawer-container glass-effect">
    <!-- Drawer Header -->
    <div class="q-pa-lg q-mb-sm row items-center border-bottom-subtle bg-drawer-header">
      <q-icon name="img:icons/favicon.svg" size="36px" class="q-mr-sm" />
      <q-space />
      <q-btn flat round dense icon="close" color="grey-7" @click="drawerState = false" />
    </div>

    <!-- Drawer Content -->
    <div class="col scroll q-px-sm">
      <q-list class="q-py-sm">
        <DrawerSubGroup>Browse</DrawerSubGroup>
        <DrawerItem
          icon="event"
          icon-color="primary"
          label="Seasons"
          forward-name="seasons"
        />
        <DrawerItem icon="people_alt" icon-color="primary" label="Players" forward-name="players" />
        <DrawerItem icon="query_stats" icon-color="primary" label="Statistics" forward-name="statistics" />

        <q-separator class="q-my-sm drawer-separator" />
        <DrawerSubGroup>Info</DrawerSubGroup>
        <DrawerItem icon="menu_book" icon-color="primary" label="Rules" forward-name="rules" />
        <DrawerItem icon="info" icon-color="primary" label="About" forward-name="about" />
 
        <q-separator class="q-my-sm drawer-separator" />
        <DrawerSubGroup>Contribute</DrawerSubGroup>
        <DrawerItem icon="forum" icon-color="primary" label="Feedback" forward-name="feedback" />
        <DrawerItem icon="view_kanban" icon-color="primary" label="Task Board" forward-name="taskboard" />

        <template v-if="isAdmin">
          <q-separator class="q-my-sm drawer-separator" />
          <DrawerSubGroup>Management</DrawerSubGroup>
          <DrawerItem
            v-if="currentSeasonId"
            icon="settings_applications"
            icon-color="primary"
            label="Current Season"
            :forward-params="{ id: currentSeasonId }"
            forward-name="season-manage"
          />
          <DrawerItem icon="sports_esports" icon-color="primary" label="Games" forward-name="games" />
          <DrawerItem
            icon="mark_email_unread"
            icon-color="primary"
            label="Invitations"
            forward-name="invitations"
          />
        </template>

      </q-list>
    </div>

    <div class="q-pa-md q-pb-xl">
      <q-separator class="q-mb-md drawer-separator" />
      <DrawerItem icon="exit_to_app" icon-color="red-7" label="Logout" class="logout-item" @click="doLogout" />
    </div>
  </div>
</template>

<script setup lang="ts">
import DrawerItem from 'components/base/DrawerItem.vue';
import DrawerSubGroup from 'components/base/DrawerSubGroup.vue';
import { useUserStore } from 'stores/userStore';
import { useHomeSeasonStore } from 'stores/homeSeasonStore';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';
import { provide, watch } from 'vue';

const drawerState = defineModel();

const { logout } = useUserStore();
const userStore = useUserStore();
const { isAdmin } = storeToRefs(userStore);

const homeSeasonStore = useHomeSeasonStore();
const { currentSeasonId } = storeToRefs(homeSeasonStore);

const router = useRouter();

provide('closeDrawer', () => (drawerState.value = false));

watch(isAdmin, (val) => {
  if (val) {
    void homeSeasonStore.init();
  }
}, { immediate: true });

async function doLogout(): Promise<void> {
  await logout();
  drawerState.value = false;
  await router.push({ name: 'home' });
}
</script>

<style lang="scss">
.kenner-drawer-container {
}

.bg-drawer-header {
}

.glass-effect {
  border-left: 1px solid rgba(0, 0, 0, 0.05);
  border-bottom: none !important;
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

.kenner-drawer {
}
</style>

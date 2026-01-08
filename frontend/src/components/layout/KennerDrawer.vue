<template>
  <div class="column full-height">
    <!-- Drawer Header -->
    <div class="q-pa-md row items-center justify-between border-bottom-subtle bg-white">
      <div class="row items-center">
        <q-icon name="menu" color="grey-7" size="sm" class="q-mr-sm" />
        <div class="text-h6 text-weight-bold text-grey-8">Menu</div>
      </div>
      <q-btn flat round dense icon="chevron_right" size="sm" color="grey-7" @click="drawerState = false">
        <q-tooltip>Minimize Menu</q-tooltip>
      </q-btn>
    </div>

    <!-- Drawer Content -->
    <div class="col scroll bg-white">
      <q-list class="q-py-md">
        <DrawerSubGroup> General </DrawerSubGroup>
        <DrawerItem icon="feedback" label="Feedback" forward-name="feedback" />

        <q-separator class="q-my-md border-subtle" inset />

        <template v-if="isAdmin">
          <DrawerSubGroup>Admin</DrawerSubGroup>
          <DrawerItem icon="casino" label="Games" forward-name="games" />
          <DrawerItem icon="group" label="Members" forward-name="users" />
          <DrawerItem
            icon="forward_to_inbox"
            label="Invitations"
            forward-name="invitations"
          />
          <DrawerItem
            icon="calendar_month"
            label="Seasons"
            forward-name="seasons"
          />
          <q-separator class="q-my-md border-subtle" inset />
        </template>

        <template v-if="isAdmin">
          <DrawerSubGroup>Dev</DrawerSubGroup>
          <DrawerItem icon="build" label="Hijack" forward-name="dev" />
          <q-separator class="q-my-md border-subtle" inset />
        </template>
      </q-list>
    </div>

    <q-list class="q-pb-lg bg-white">
      <DrawerItem icon="logout" label="Logout" @click="doLogout" />
    </q-list>
  </div>
</template>

<script setup lang="ts">
import DrawerItem from 'components/base/DrawerItem.vue';
import { useUserStore } from 'stores/userStore';
import { useResponsive } from 'src/composables/responsive';
import DrawerSubGroup from 'components/base/DrawerSubGroup.vue';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';
import { provide } from 'vue';

const drawerState = defineModel();

const responsive = useResponsive();
const { logout } = useUserStore();
const { isAdmin } = storeToRefs(useUserStore());

const { isMobile } = responsive;
const router = useRouter();

provide('closeDrawer', () => (drawerState.value = false));

async function doLogout(): Promise<void> {
  await logout();
  drawerState.value = false;
  await router.push({ name: 'home' });
}
</script>

<style lang="scss">
.kenner-drawer {
  border-left: 2px solid #cfd8dc !important;
}

.border-subtle {
  border-color: rgba(0, 0, 0, 0.05);
}
</style>

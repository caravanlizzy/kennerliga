<template>
  <div class="column full-height kenner-drawer-container">
    <!-- Drawer Content -->
    <div class="col scroll">
      <q-list class="q-py-sm">
        <DrawerSubGroup> General </DrawerSubGroup>
        <DrawerItem icon="feedback" icon-color="orange-8" label="Feedback" forward-name="feedback" />

        <q-separator class="q-my-sm drawer-separator" inset />

        <template v-if="isAdmin">
          <DrawerSubGroup>Management</DrawerSubGroup>
          <DrawerItem icon="casino" icon-color="indigo-7" label="Games" forward-name="games" />
          <DrawerItem icon="group" icon-color="teal-7" label="Members" forward-name="users" />
          <DrawerItem
            icon="forward_to_inbox"
            icon-color="deep-purple-7"
            label="Invitations"
            forward-name="invitations"
          />
          <DrawerItem
            icon="calendar_month"
            icon-color="blue-8"
            label="Seasons"
            forward-name="seasons"
          />
          <q-separator class="q-my-sm drawer-separator" inset />
        </template>

        <template v-if="isAdmin">
          <DrawerSubGroup>Development</DrawerSubGroup>
          <DrawerItem icon="terminal" icon-color="grey-9" label="Hijack (Dev)" forward-name="dev" />
          <q-separator class="q-my-sm drawer-separator" inset />
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
.kenner-drawer-container {
  background-color: #fbfbfb;
}

.drawer-separator {
  opacity: 0.5;
}

.kenner-drawer {
  border-left: 2px solid #cfd8dc !important;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.02);
}
</style>

<template>
  <div>
    <q-drawer
      side="right"
      v-model="drawerState"
      :mini="isMobile"
      :width="240"
      :mini-width="80"
      class="kenner-drawer"
    >
      <div class="column full-height">
        <q-list class="col q-py-md">
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

        <q-list class="q-pb-lg">
          <DrawerItem icon="logout" label="Logout" @click="doLogout" />
        </q-list>
      </div>
    </q-drawer>
    <!--    <DevUsersList :show-impersonate="showImpersonateList" />-->
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
  background: rgba(255, 255, 255, 0.6) !important;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-left: 1px solid rgba(0, 0, 0, 0.05) !important;
}

.border-subtle {
  border-color: rgba(0, 0, 0, 0.05);
}
</style>

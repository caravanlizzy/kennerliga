<template>
  <div>
    <q-drawer
      bordered
      side="right"
      v-model="drawerState"
      :mini="isMobile"
      :width="220"
    >
      <q-list>
        <DrawerItem icon="feedback" label="Feedback" forward-name="feedback" />

        <q-separator class="q-my-sm" />

        <template v-if="isAdmin">
          <DrawerSubGroup>Admin</DrawerSubGroup>
          <DrawerItem icon="casino" label="Games" forward-name="games" />
          <DrawerItem icon="group" label="Members" forward-name="users" />
          <DrawerItem
            icon="calendar_month"
            label="Seasons"
            forward-name="seasons"
          />
          <q-separator class="q-my-sm" />

        </template>


        <DrawerSubGroup>Dev</DrawerSubGroup>
        <DrawerItem icon="build" label="Hijack" forward-name="dev" />

        <q-separator class="q-my-sm" />

        <DrawerItem icon="logout" label="Logout" @click="logout" />
      </q-list>
    </q-drawer>
    <!--    <DevUsersList :show-impersonate="showImpersonateList" />-->
  </div>
</template>

<script setup lang="ts">
import DrawerItem from 'components/base/DrawerItem.vue';
import { useUserStore } from 'stores/userStore';
import { useResponsive } from 'src/composables/reponsive';
import DrawerSubGroup from 'components/base/DrawerSubGroup.vue';
import { storeToRefs } from 'pinia';

const drawerState = defineModel();

const responsive = useResponsive();
const { logout } = useUserStore();
const { isAdmin } = storeToRefs(useUserStore());

const { isMobile } = responsive;
</script>

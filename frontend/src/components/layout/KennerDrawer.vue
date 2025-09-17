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
        <kenner-item
          icon="settings"
          label="Settings"
          forward-name="settings"
        />
        <kenner-item
          icon="account_circle"
          label="Profile"
          forward-name="profile"
        />
        <kenner-item
          icon="casino"
          label="Games"
          forward-name="games"
        />
        <kenner-item
          icon="group"
          label="Users"
          forward-name="users"
        />
        <kenner-item icon="logout" label="Logout" @click="logout" />
      </q-list>
    </q-drawer>
<!--    <DevUsersList :show-impersonate="showImpersonateList" />-->
  </div>
</template>

<script setup lang="ts">
import KennerItem from 'components/base/KennerItem.vue';
import { useUserStore } from 'stores/userStore';
import { useResponsive } from 'src/composables/reponsive';

const drawerState = defineModel();


const responsive = useResponsive();
const { logout } = useUserStore();

const { isMobile } = responsive;
</script>

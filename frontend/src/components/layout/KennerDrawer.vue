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
        <KennerItem
          icon="calendar_month"
          label="Seasons"
          forward-name="seasons"
          />
        <KennerItem
          icon="casino"
          label="Games"
          forward-name="games"
        />
        <KennerItem
          icon="group"
          label="Members"
          forward-name="users"
        />
        <KennerItem icon="logout" label="Logout" @click="logout" />
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

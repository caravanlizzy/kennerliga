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
          label="Einstellungen"
          forward-name="settings"
        />
        <kenner-item
          icon="account_circle"
          label="Profil"
          forward-name="profile"
        />
        <kenner-item
          icon="casino"
          label="Spiele verwalten"
          forward-name="games"
        />
        <kenner-item
          icon="group"
          label="SpielerInnen verwalten"
          forward-name="users"
        />
        <kenner-item
          icon="switch_account"
          label="Impersonate User"
          @click="showImpersonateList = !showImpersonateList"
        >
        </kenner-item>
        <kenner-item icon="logout" label="Logout" @click="logout" />
      </q-list>
    </q-drawer>
    <DevUsersList :show-impersonate="showImpersonateList" />
  </div>
</template>

<script setup lang="ts">
import KennerItem from 'components/items/KennerItem.vue';
import { useUserStore } from 'stores/userStore';
import { useResponsive } from 'src/composables/reponsive';
import { ref } from 'vue';
import DevUsersList from 'components/lists/DevUsersList.vue';

const drawerState = defineModel();

const showImpersonateList = ref(false)

const responsive = useResponsive();
const { logout } = useUserStore();

const { isMobile } = responsive;
</script>

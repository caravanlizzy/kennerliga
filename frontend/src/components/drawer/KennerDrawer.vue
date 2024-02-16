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
        <kenner-item icon="settings" label="Einstellungen" forward-name="settings" />
        <kenner-item icon="account_circle" label="Profil" forward-name="profile" />
        <kenner-item icon="casino" label="Spiele verwalten" forward-name="games" />
        <kenner-item icon="group" label="SpielerInnen verwalten" forward-name="users" />
        <kenner-item icon="logout" label="Logout" />
      </q-list>
    </q-drawer>
  </div>
</template>

<script setup lang="ts">
import KennerItem from 'components/items/KennerItem.vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import { useResponsive } from 'src/composables/reponsive';

const drawerState = defineModel();

const responsive = useResponsive();

const { isMobile } = responsive;
</script>

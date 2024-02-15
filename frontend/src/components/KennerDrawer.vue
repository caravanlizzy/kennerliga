<template>
  <div>
    <q-drawer
      elevated
      overlay
      side="right"
      v-model="drawerState"
      width="250"
      mini-width="70"
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
import KennerItem from 'components/KennerItem.vue';
const drawerState = defineModel();
</script>

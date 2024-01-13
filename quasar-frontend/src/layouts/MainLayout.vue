<template>
  <q-layout view="hHh Lpr lFf">
    <q-header elevated>
      <q-toolbar class="bg-primary">
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title>
          Kennerliga
        </q-toolbar-title>

        <ToolbarTop />
<!--        <div>Kennerliga</div>-->
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
    >
      <q-list>
        <q-item-label
          header
        >
          Verwaltung
        </q-item-label>

        <AdminSidebar
          v-for="link in adminLinks"
          :key="link.title"
          v-bind="link"
        />
      </q-list>
    </q-drawer>

    <q-page-container >
        <router-view class="q-pa-md" />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import AdminSidebar, { AdminLinkProps } from 'components/AdminSidebar.vue';
import ToolbarTop from 'components/ToolbarTop.vue';

const adminLinks: AdminLinkProps[] = [
  {
    title: 'Spieler',
    caption: 'Accounts verwalten',
    icon: 'manage_accounts',
    routeName: 'users'
  },
  {
    title: 'Spiele',
    caption: 'Spiele verwalten',
    icon: 'casino',
    routeName: 'games'
  },
  {
    title: 'Seasons',
    caption: 'Seasons/Ligen verwalten',
    icon: 'calendar_month',
    routeName: 'season'
  },
  {
    title: 'Kommunikation',
    caption: 'Öffentliche verwalten',
    icon: 'feed',
    routeName: 'feeds'
  }
];

const leftDrawerOpen = ref(false)

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value
}
</script>

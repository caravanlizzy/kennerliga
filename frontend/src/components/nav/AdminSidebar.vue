<template>
  <q-drawer side="right" :model-value="drawerOpen" bordered mini class="bg-primary">
    <q-list>
      <q-item-label header>
        Verwaltung
      </q-item-label>

      <AdminSidebarEntry class="text-info" v-for="link in adminLinks" :key="link.title" v-bind="link" />
    </q-list>
  </q-drawer>
</template>

<script setup lang="ts">
import AdminSidebarEntry, { AdminLinkProps } from 'components/nav/AdminSidebarEntry.vue';

defineProps<{
  drawerOpen: boolean
}>()

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

</script>

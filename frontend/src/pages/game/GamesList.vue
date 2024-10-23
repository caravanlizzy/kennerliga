<template>
  <KennerligaTable
    v-if="isFinished && isPlatformFinished"
    :create-button="button"
    flat
    title="Spiele"
    @row-click="onRowClick"
    :rows="data"
    :columns="columns"
    :rows-per-page-options="[10, 20, 50]"/>
</template>

<script setup lang="ts">
import KennerligaTable from 'components/tables/KennerTable.vue';
import { useAxios } from '@vueuse/integrations/useAxios';
import { api } from 'boot/axios';
import { useRouter } from 'vue-router';
import { TKennerButton } from 'src/models/models';
import { ref, computed, watch, onMounted } from 'vue';

// Fetching games data
const { data, isFinished } = useAxios('game/games', api);

// Fetching platforms data to create platformMap
const platformMap = ref<{ [key: string]: string }>({});
const { data: platformData, isFinished: isPlatformFinished } = useAxios('game/platforms', api);

onMounted(() => {
  watch(() => isPlatformFinished.value, (newVal) => {
    if (newVal && platformData.value) {
      // Creating a map of platform IDs to platform names
      platformMap.value = platformData.value.reduce((map: any, platform: { id: string, name: string }) => {
        map[platform.id] = platform.name;
        return map;
      }, {});
    }
  });
});

// Router for navigation on row click
const router = useRouter();
const onRowClick = (_event: never, row: { id: never; }) => {
  router.push({ name: 'game-detail', params: { id: row.id } });
};

// Button configuration
const button: TKennerButton = { color: 'secondary', label: 'Spiel', icon: 'add_circle', forwardName: 'game-create' };

// Reactive columns definition that depends on platformMap
const columns = computed(() => [
  {
    name: 'game',
    required: true,
    align: 'left',
    label: 'Spiel',
    field: (x: { name: never; }) => x.name,
    sortable: true
  },
  {
    name: 'platform',
    label: 'Plattform',
    required: false,
    align: 'center',
    // Using platformMap to get the platform name from the platform ID
    field: (x: { platform: string; }) => platformMap.value[x.platform] || 'Unknown Platform',
    sortable: true
  }
]);

</script>

<template>
    <KennerligaTable v-if="isFinished" flat title="Spiele" @row-click="onRowClick" :rows="data" :columns="columns" :rows-per-page-options="[10, 20, 50]"/>
</template>


<script setup lang="ts">
import KennerligaTable from 'components/KennerligaTable.vue';
import { useAxios } from '@vueuse/integrations/useAxios';

import { api } from 'boot/axios';
import { useRouter } from 'vue-router';

const { data , isFinished } = useAxios('games', api);

const router = useRouter();

const onRowClick = (_event, row) => {
  router.push({name: 'game-detail', params: { id: row.id }});
}
const columns = [
  {
    name: 'game',
    required: true,
    align: 'left',
    label: 'Spiel',
    field: x => x.name,
    sortable: true,
  },
  {
    name: 'platform',
    label: 'Plattform',
    required: false,
    align: 'center',
    field: x => x.platform,
    sortable: true,
  }
]


</script>

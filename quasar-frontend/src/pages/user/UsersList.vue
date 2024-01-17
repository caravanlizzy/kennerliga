<template>

  <KennerligaTable v-if="isFinished" flat title="SpielerInnen" @row-click="onRowClick" :rows="data" :row-key="id" :columns="columns" :rows-per-page-options="[10, 20, 50]"/>
</template>

<script setup lang="ts">
import KennerligaTable from 'components/KennerligaTable.vue';
import { useAxios } from '@vueuse/integrations/useAxios';
import { api } from 'boot/axios';
import { useRouter } from 'vue-router';

const { data , isFinished } = useAxios('users', api);

const router = useRouter();

const onRowClick = (_event, row) => {
  router.push({name: 'user-detail', params: { id: row.id }});
}

const columns = [
  {
    name: 'user',
    required: true,
    align: 'left',
    label: 'Name',
    field: x => x.username,
    sortable: true,
  },
  {
    name: 'bga_name',
    label: 'BGA Name',
    required: false,
    align: 'center',
    field: x => x.bga_name,
    sortable: true,
  },
  {
    name: 'email',
    label: 'Email',
    required: false,
    align: 'right',
    field: x => x.email,
    sortable: true,
  }
]
</script>

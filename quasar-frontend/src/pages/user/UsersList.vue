<template>

  <KennerligaTable v-if="isFinished" flat title="SpielerInnen" :rows="data" :columns="columns" :rows-per-page-options="[10, 20, 50]"/>
</template>

<script setup lang="ts">
import KennerligaTable from 'components/KennerligaTable.vue';
import { useAxios } from '@vueuse/integrations/useAxios';
import { api } from 'boot/axios';

const { data , isFinished } = useAxios('users', api);

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
    align: 'enter',
    field: x => x.email,
    sortable: true,
  }
]
</script>

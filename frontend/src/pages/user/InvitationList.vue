<template>
  <KennerligaTable
    v-if="isFinished"
    flat
    title="Invitations"
    :rows="data"
    :columns="columns"
    :rows-per-page-options="[10, 20, 50]"
  />
</template>

<script setup lang="ts">
import KennerligaTable from 'components/tables/KennerTable.vue';
import { useAxios } from '@vueuse/integrations/useAxios';
import { api } from 'boot/axios';

const { data, isFinished } = useAxios('user/invitations/', api);

const columns = [
  {
    name: 'username',
    required: true,
    align: 'left',
    label: 'Username',
    field: (x) => x.username,
    sortable: true,
  },
  {
    name: 'otp',
    required: true,
    align: 'center',
    label: 'OTP',
    field: (x) => x.otp,
    sortable: true,
  },
  {
    name: 'failed_attempts',
    required: true,
    align: 'right',
    label: 'Failed Attempts',
    field: (x) => x.failed_attempts,
    sortable: true,
  },
];
</script>

<template>
  <KennerTable
    v-if="data"
    flat
    title="Invitations"
    :rows="data"
    :columns="columns"
    :rows-per-page-options="[10, 20, 50]"
    :createButton="createBtn"
  />
</template>

<script setup lang="ts">
import KennerTable from 'components/tables/KennerTable.vue';
import { api } from 'boot/axios';
import type { TKennerButton } from 'src/types';

const { data } = await api('user/invitations/');

const createBtn: TKennerButton = {
  color: 'secondary',
  label: 'Invite',
  icon: 'add_circle',
  forwardName: 'invite-user',
};

const columns = [
  {
    name: 'label',
    required: true,
    align: 'left',
    label: 'Internal Note',
    field: (x) => x.label,
    sortable: true,
  },
  {
    name: 'invite_url',
    required: true,
    align: 'left',
    label: 'Invite URL',
    field: (x) => x.invite_url,
    sortable: true,
  },
];
</script>

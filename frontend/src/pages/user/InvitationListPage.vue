<template>
    <KennerTable
      v-if="data"
      flat
      title="Invitations"
      :rows="data"
      :columns="columns"
      :createButton="createBtn"
    >
      <template #body-cell-invite_url="props">
        <q-td :props="props">
          <q-btn
            flat
            round
            dense
            icon="content_copy"
            @click="copyInviteUrl(props.row.invite_url)"
          />
        </q-td>
      </template>
    </KennerTable>
</template>

<script setup lang="ts">
import KennerTable from 'components/tables/KennerTable.vue';
import { api } from 'boot/axios';
import type { TKennerButton } from 'src/types';
import { copyToClipboard, useQuasar } from 'quasar';

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
    label: 'Registration Link',
    field: (x) => x.invite_url,
    sortable: true,
  },
];

const $q = useQuasar();

function copyInviteUrl(url: string) {
  copyToClipboard(url)
    .then(() => $q.notify({ type: 'positive', message: 'Copied!' }))
    .catch(() => $q.notify({ type: 'negative', message: 'Copy failed' }));
}
</script>

<template>
  <KennerTable
    v-if="!loading && !error && data"
    flat
    :rows="data"
    :columns="columns"
    :createButton="createBtn"
  >
    <template #body-cell-type="props">
      <q-td :props="props">
        <q-chip
          dense
          size="sm"
          :color="props.row.type === 'password' ? 'amber-2' : 'blue-2'"
          :text-color="props.row.type === 'password' ? 'amber-9' : 'primary'"
          :icon="props.row.type === 'password' ? 'lock_reset' : 'person_add'"
          class="text-weight-bold"
        >
          {{ props.row.type === 'password' ? 'Password' : 'Invitation' }}
        </q-chip>
      </q-td>
    </template>
    <template #body-cell-invite_url="props">
      <q-td :props="props">
        <KennerButton
          flat
          round
          dense
          icon="content_copy"
          @click="copyInviteUrl(props.row.invite_url)"
        >
          <q-tooltip>Copy link</q-tooltip>
        </KennerButton>
      </q-td>
    </template>
  </KennerTable>
</template>

<script setup lang="ts">
import KennerTable from 'components/tables/KennerTable.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { fetchInvitations } from 'src/services/userService';
import type { TKennerButton, TUserInviteDto } from 'src/types';
import { copyToClipboard, useQuasar } from 'quasar';
import { useAsyncData } from 'src/composables/asyncData';
import { computed } from 'vue';

const { data, isFinished, error } = useAsyncData(
  fetchInvitations,
  [] as TUserInviteDto[]
);
const loading = computed(() => !isFinished.value);

const createBtn: TKennerButton = {
  color: 'secondary',
  label: 'Invite',
  icon: 'add_circle',
  forwardName: 'invite-user',
};

const columns = [
  {
    name: 'type',
    required: true,
    align: 'left' as const,
    label: 'Type',
    field: (x: TUserInviteDto) => x.type || 'invitation',
    sortable: true,
  },
  {
    name: 'label',
    required: true,
    align: 'left' as const,
    label: 'Internal Note / Target',
    field: (x: TUserInviteDto) => x.label,
    sortable: true,
  },
  {
    name: 'invite_url',
    required: true,
    align: 'left' as const,
    label: 'Link',
    field: (x: TUserInviteDto) => x.invite_url,
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

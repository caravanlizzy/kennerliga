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
    <template #body-cell-actions="props">
      <q-td :props="props" auto-width class="q-gutter-x-xs">
        <KennerButton
          flat
          round
          dense
          icon="content_copy"
          color="primary"
          @click.stop="copyInviteUrl(props.row.invite_url)"
        >
          <q-tooltip>Copy link</q-tooltip>
        </KennerButton>
        <KennerButton
          flat
          round
          dense
          icon="delete"
          color="negative"
          @click.stop="onDelete(props.row)"
        >
          <q-tooltip>Delete</q-tooltip>
        </KennerButton>
      </q-td>
    </template>
  </KennerTable>

  <div v-else-if="error" class="q-py-md">
    <q-banner rounded dense class="q-mb-sm text-negative">
      <template #avatar><q-icon name="warning" color="negative" /></template>
      {{ error.message || 'Failed to load invitations.' }}
    </q-banner>
  </div>
  <div v-else class="q-py-md">
    <q-skeleton height="180px" square />
  </div>
</template>

<script setup lang="ts">
import KennerTable from 'components/tables/KennerTable.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { fetchInvitations, deleteInvitation } from 'src/services/userService';
import type { TKennerButton, TUserInviteDto } from 'src/types';
import { copyToClipboard, useQuasar } from 'quasar';
import { useAsyncData } from 'src/composables/asyncData';
import { useDialog } from 'src/composables/dialog';
import { computed } from 'vue';

const { data, isFinished, error, reload } = useAsyncData(
  fetchInvitations,
  [] as TUserInviteDto[]
);
const loading = computed(() => !isFinished.value);
const { setDialog } = useDialog();

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
    name: 'actions',
    required: true,
    align: 'right' as const,
    label: 'Actions',
    field: () => '',
  },
];

const $q = useQuasar();

function copyInviteUrl(url: string) {
  copyToClipboard(url)
    .then(() => $q.notify({ type: 'positive', message: 'Copied!' }))
    .catch(() => $q.notify({ type: 'negative', message: 'Copy failed' }));
}

function onDelete(row: TUserInviteDto) {
  const isPassword = row.type === 'password';
  const itemType = isPassword ? 'password reset link' : 'invitation link';
  const labelText = row.label ? ` "${row.label}"` : '';

  setDialog(
    `Confirm Delete ${isPassword ? 'Password Reset' : 'Invitation'}`,
    `Are you sure you want to delete the ${itemType}${labelText}?`,
    'warning',
    async () => {
      try {
        await deleteInvitation(row.id);
        $q.notify({
          type: 'positive',
          message: `${isPassword ? 'Password reset' : 'Invitation'} deleted successfully.`,
        });
        await reload();
      } catch (e: any) {
        $q.notify({
          type: 'negative',
          message: e?.response?.data?.detail || e?.message || 'Failed to delete.',
        });
      }
    },
    undefined,
    'Delete'
  );
}
</script>

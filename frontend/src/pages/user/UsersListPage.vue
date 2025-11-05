<template>
  <KennerligaTable
    v-if="isFinished"
    :create-button="button"
    flat
    title="Kennerliga Members"
    @row-click="onRowClick"
    :rows="users"
    :columns="columns"
    :rows-per-page-options="[10, 20, 50]"
  />
</template>

<script setup lang="ts">
import KennerligaTable from 'components/tables/KennerTable.vue';
import { useRouter } from 'vue-router';
import { TKennerButton, TUser } from 'src/types';
import { onMounted, ref } from 'vue';
import { useUserStore } from 'stores/userStore';

const { listUsers } = useUserStore();
const users = ref<TUser[]>([]);

onMounted(async () => {
  users.value = await listUsers();
});

const router = useRouter();

const onRowClick = (_event: never, row: { username: never }) => {
  router.push({ name: 'user-detail', params: { username: row.username } });
};

const button: TKennerButton = {
  color: 'secondary',
  label: 'Invite',
  icon: 'add_circle',
  forwardName: 'user-invite',
};

const columns = [
  {
    name: 'user',
    required: true,
    align: 'left',
    label: 'Name',
    field: (x: TUser) => x.username,
    sortable: true,
  },
  {
    name: 'bga_name',
    label: 'BGA Name',
    required: false,
    align: 'center',
    field: (x: TUser) => x.bga_name,
    sortable: true,
  },
];
</script>

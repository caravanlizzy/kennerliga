<template>
  <KennerligaTable
    :create-button="createButton"
    flat
    title="Kennerliga Members"
    @row-click="onRowClick"
    :rows="users"
    :columns="columns"
  />
</template>

<script setup lang="ts">
import KennerligaTable from 'components/tables/KennerTable.vue';
import { useRouter } from 'vue-router';
import { TKennerButton, TUserDto } from 'src/types';
import { onMounted, ref } from 'vue';
import { useUserStore } from 'stores/userStore';

const { listUsers } = useUserStore();
const users = ref<TUserDto[]>([]);

onMounted(async () => {
  users.value = await listUsers();
});

const router = useRouter();

const onRowClick = (_event: never, row: { username: never }) => {
  router.push({ name: 'user-detail', params: { username: row.username } });
};

const createButton: TKennerButton = {
  color: 'secondary',
  label: 'Invite',
  icon: 'add_circle',
  forwardName: 'invite-user',
};

const columns = [
  {
    name: 'user',
    required: true,
    align: 'left',
    label: 'Name',
    field: (x: TUserDto) => x.username,
    sortable: true,
  },
];
</script>

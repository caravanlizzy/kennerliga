<template>
  <KennerTable
    :create-button="createButton"
    flat
    title="Users"
    @row-click="onRowClick"
    :rows="users"
    :columns="columns"
  >
    <template v-slot:body-cell-most_participated_league_level="props">
      <q-td :props="props">
        <LeagueLevel
          v-if="props.row.most_participated_league_level"
          badge
          :level="props.row.most_participated_league_level"
        />
        <span v-else class="text-grey-5">-</span>
      </q-td>
    </template>
  </KennerTable>
</template>

<script setup lang="ts">
import KennerTable from 'components/tables/KennerTable.vue';
import LeagueLevel from 'components/season/LeagueLevel.vue';
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
  {
    name: 'win_rate',
    align: 'right',
    label: 'Win %',
    field: (x: TUserDto) => x.win_rate,
    format: (val: number | null | undefined) =>
      val !== null && val !== undefined ? `${val.toFixed(1)}%` : '-',
    sortable: true,
  },
  {
    name: 'avg_position',
    align: 'right',
    label: 'Avg Pos',
    field: (x: TUserDto) => x.avg_position,
    format: (val: number | null | undefined) =>
      val !== null && val !== undefined ? val.toFixed(2) : '-',
    sortable: true,
  },
  {
    name: 'most_participated_league_level',
    align: 'right',
    label: 'Most Played League',
    field: (x: TUserDto) => x.most_participated_league_level,
    format: (val: number | null | undefined) =>
      val !== null && val !== undefined ? `L${val}` : '-',
    sortable: true,
  },
];
</script>

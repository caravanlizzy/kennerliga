<template>
  <div class="q-mb-md row items-center justify-between q-gutter-sm">
    <div class="row items-center q-gutter-x-sm">
      <span class="text-caption text-weight-bold text-grey-7">Filter Games:</span>
      <q-chip
        clickable
        v-model:selected="exclude2p"
        :color="exclude2p ? 'primary' : 'grey-3'"
        :text-color="exclude2p ? 'white' : 'grey-8'"
        icon="filter_alt"
        class="text-weight-medium"
      >
        Exclude 2P Only
      </q-chip>
      <q-chip
        clickable
        v-model:selected="exclude3p"
        :color="exclude3p ? 'primary' : 'grey-3'"
        :text-color="exclude3p ? 'white' : 'grey-8'"
        icon="filter_alt"
        class="text-weight-medium"
      >
        Exclude 3P Only
      </q-chip>
    </div>
  </div>

  <KennerTable
    :create-button="createButton"
    flat
    title="Users"
    @row-click="onRowClick"
    :rows="users"
    :columns="columns"
    :loading="loading"
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
import { onMounted, ref, watch } from 'vue';
import { useUserStore } from 'stores/userStore';

const { listUsers } = useUserStore();
const users = ref<TUserDto[]>([]);
const exclude2p = ref(false);
const exclude3p = ref(false);
const loading = ref(false);

async function loadUsers() {
  loading.value = true;
  try {
    const params: Record<string, boolean> = {};
    if (exclude2p.value) params.exclude_2p_only = true;
    if (exclude3p.value) params.exclude_3p_only = true;
    users.value = (await listUsers(params)) ?? [];
  } finally {
    loading.value = false;
  }
}

watch([exclude2p, exclude3p], () => {
  loadUsers();
});

onMounted(() => {
  loadUsers();
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

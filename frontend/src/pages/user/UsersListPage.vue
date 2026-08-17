<template>
  <div class="q-mb-md row items-center justify-between q-gutter-sm">
    <div class="row items-center q-gutter-md">
      <!-- Player Count Settings Filter -->
      <div class="row items-center q-gutter-x-sm">
        <span class="text-caption text-weight-bold text-grey-7">Player Count:</span>
        <q-btn-toggle
          v-model="playerCount"
          dense
          no-caps
          rounded
          unelevated
          toggle-color="primary"
          color="grey-3"
          text-color="grey-8"
          toggle-text-color="white"
          :options="[
            { label: 'All', value: 'all' },
            { label: '2P', value: '2p' },
            { label: '3P', value: '3p' },
            { label: '4P', value: '4p' }
          ]"
        />
      </div>

      <!-- Years Multi-select Filter -->
      <div class="row items-center q-gutter-x-sm">
        <span class="text-caption text-weight-bold text-grey-7">Years:</span>
        <q-select
          v-model="selectedYears"
          :options="availableYears"
          multiple
          clearable
          dense
          outlined
          options-dense
          placeholder="All Years"
          :display-value="!selectedYears || selectedYears.length === 0 ? 'All Years' : selectedYears.slice().sort((a, b) => b - a).join(', ')"
          style="min-width: 170px"
          class="bg-white rounded-borders"
        >
          <template v-slot:prepend>
            <q-icon name="calendar_today" size="xs" />
          </template>
        </q-select>
      </div>
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

const { listUsers, getAvailableYears } = useUserStore();
const users = ref<TUserDto[]>([]);
const playerCount = ref<'all' | '2p' | '3p' | '4p'>('all');
const selectedYears = ref<number[]>([]);
const availableYears = ref<number[]>([]);
const loading = ref(false);

async function loadUsers() {
  loading.value = true;
  try {
    const params: Record<string, string> = {};
    if (playerCount.value && playerCount.value !== 'all') {
      params.player_count = playerCount.value;
    }
    if (selectedYears.value && selectedYears.value.length > 0) {
      params.years = selectedYears.value.join(',');
    }
    users.value = (await listUsers(params)) ?? [];
  } finally {
    loading.value = false;
  }
}

watch([playerCount, selectedYears], () => {
  loadUsers();
});

onMounted(async () => {
  const years = await getAvailableYears();
  if (years && years.length > 0) {
    availableYears.value = years;
  }
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

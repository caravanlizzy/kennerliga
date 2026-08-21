<template>
  <div class="q-mb-md filter-toolbar">
    <div class="filter-controls row items-center q-col-gutter-md">
      <!-- Player Count Filter -->
      <div class="filter-item row items-center q-gutter-x-sm">
        <div class="row items-center text-caption text-weight-bold text-grey-8 filter-label">
          <q-icon name="groups" size="18px" class="q-mr-xs text-primary" />
          <span>Players:</span>
        </div>
        <div class="row q-gutter-xs items-center">
          <q-chip
            clickable
            dense
            :outline="!isAllPlayerCountsSelected"
            :color="isAllPlayerCountsSelected ? 'primary' : 'grey-7'"
            text-color="white"
            size="sm"
            class="text-weight-bold"
            style="border-radius: 4px"
            @click="toggleAllPlayerCounts"
          >
            All
          </q-chip>
          <q-chip
            v-for="pc in availablePlayerCounts"
            :key="pc"
            clickable
            dense
            :outline="!selectedPlayerCounts.includes(pc)"
            :color="selectedPlayerCounts.includes(pc) ? 'primary' : 'grey-7'"
            text-color="white"
            size="sm"
            class="text-weight-bold"
            style="border-radius: 4px"
            @click="togglePlayerCount(pc)"
          >
            {{ pc.toUpperCase() }}
          </q-chip>
        </div>
      </div>

      <!-- Years Multi-select Filter -->
      <div class="filter-item row items-center q-gutter-x-sm">
        <div class="row items-center text-caption text-weight-bold text-grey-8 filter-label">
          <q-icon name="calendar_today" size="16px" class="q-mr-xs text-primary" />
          <span>Years:</span>
        </div>
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
          class="bg-white rounded-borders years-select"
        >
          <template v-slot:prepend>
            <q-icon name="event" size="xs" color="grey-6" />
          </template>
        </q-select>
      </div>
    </div>
  </div>

  <KennerTable
    :create-button="createButton"
    flat
    @row-click="onRowClick"
    :rows="users"
    :columns="columns"
    :loading="loading"
  >
    <template v-slot:body-cell-win_rate="props">
      <q-td :props="props">
        <div class="row items-center justify-end no-wrap q-gutter-x-xs">
          <span>{{ props.value }}</span>
          <q-badge
            v-if="isBestWinRate(props.row)"
            color="positive"
            text-color="white"
            class="text-weight-bolder"
            style="font-size: 0.65rem; padding: 2px 5px; border-radius: 4px;"
            label="best"
          />
        </div>
      </q-td>
    </template>
    <template v-slot:body-cell-avg_position="props">
      <q-td :props="props">
        <div class="row items-center justify-end no-wrap q-gutter-x-xs">
          <span>{{ props.value }}</span>
          <q-badge
            v-if="isBestAvgPosition(props.row)"
            color="primary"
            text-color="white"
            class="text-weight-bolder"
            style="font-size: 0.65rem; padding: 2px 5px; border-radius: 4px;"
            label="best"
          />
        </div>
      </q-td>
    </template>
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
import { computed, onMounted, ref, watch } from 'vue';
import { useUserStore } from 'stores/userStore';

const { listUsers, getAvailableYears } = useUserStore();
const users = ref<TUserDto[]>([]);
const availablePlayerCounts = ['2p', '3p', '4p'];
const selectedPlayerCounts = ref<string[]>(['4p']);
const isAllPlayerCountsSelected = computed(
  () => selectedPlayerCounts.value.length === 0
);
const selectedYears = ref<number[]>([]);
const availableYears = ref<number[]>([]);
const loading = ref(false);

const bestWinRate = computed(() => {
  const validUsers = users.value.filter(
    (u) => (u.total_games ?? 0) > 0 && u.win_rate !== null && u.win_rate !== undefined
  );
  if (validUsers.length === 0) return null;
  const max = Math.max(...validUsers.map((u) => u.win_rate as number));
  return max > 0 ? max : null;
});

const bestAvgPosition = computed(() => {
  const validUsers = users.value.filter(
    (u) => (u.total_games ?? 0) > 0 && u.avg_position !== null && u.avg_position !== undefined
  );
  if (validUsers.length === 0) return null;
  return Math.min(...validUsers.map((u) => u.avg_position as number));
});

function isBestWinRate(row: TUserDto) {
  return (
    bestWinRate.value !== null &&
    (row.total_games ?? 0) > 0 &&
    row.win_rate === bestWinRate.value
  );
}

function isBestAvgPosition(row: TUserDto) {
  return (
    bestAvgPosition.value !== null &&
    (row.total_games ?? 0) > 0 &&
    row.avg_position === bestAvgPosition.value
  );
}

function togglePlayerCount(val: string) {
  if (val === 'all') {
    selectedPlayerCounts.value = [];
    return;
  }
  const idx = selectedPlayerCounts.value.indexOf(val);
  if (idx >= 0) {
    selectedPlayerCounts.value.splice(idx, 1);
  } else {
    selectedPlayerCounts.value.push(val);
  }

  // If all individual player counts are selected, automatically switch to "All" (empty array)
  if (selectedPlayerCounts.value.length === availablePlayerCounts.length) {
    selectedPlayerCounts.value = [];
  }
}

function toggleAllPlayerCounts() {
  selectedPlayerCounts.value = [];
}

async function loadUsers() {
  loading.value = true;
  try {
    const params: Record<string, string> = {};
    if (selectedPlayerCounts.value.length > 0) {
      params.player_count = selectedPlayerCounts.value.join(',');
    }
    if (selectedYears.value && selectedYears.value.length > 0) {
      params.years = selectedYears.value.join(',');
    }
    users.value = (await listUsers(params)) ?? [];
  } finally {
    loading.value = false;
  }
}

watch([selectedPlayerCounts, selectedYears], () => {
  loadUsers();
}, { deep: true });

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

const sortNullableLarge = (a: number | null | undefined, b: number | null | undefined) => {
  if (a === b) return 0;
  if (a === null || a === undefined) return 1;
  if (b === null || b === undefined) return -1;
  return a - b;
};

const sortNullableSmall = (a: number | null | undefined, b: number | null | undefined) => {
  if (a === b) return 0;
  if (a === null || a === undefined) return -1;
  if (b === null || b === undefined) return 1;
  return a - b;
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
    name: 'total_games',
    align: 'right',
    label: 'Games',
    field: (x: TUserDto) => x.total_games,
    format: (val: number | null | undefined) =>
      val !== null && val !== undefined ? `${val}` : '0',
    sortable: true,
  },
  {
    name: 'win_rate',
    align: 'right',
    label: 'Win %',
    field: (x: TUserDto) => x.win_rate,
    format: (val: number | null | undefined) =>
      val !== null && val !== undefined ? `${val.toFixed(1)}%` : '-',
    sort: sortNullableSmall,
    sortable: true,
  },
  {
    name: 'avg_position',
    align: 'right',
    label: 'Avg Pos',
    field: (x: TUserDto) => x.avg_position,
    format: (val: number | null | undefined) =>
      val !== null && val !== undefined ? val.toFixed(2) : '-',
    sort: sortNullableLarge,
    sortable: true,
  },
  {
    name: 'most_participated_league_level',
    align: 'right',
    label: 'Home League',
    field: (x: TUserDto) => x.most_participated_league_level,
    format: (val: number | null | undefined) =>
      val !== null && val !== undefined ? `L${val}` : '-',
    sort: sortNullableLarge,
    sortable: true,
  },
];
</script>

<style scoped lang="scss">
.filter-toolbar {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(54, 64, 88, 0.08);
  border-radius: 12px;
  padding: 10px 16px;
}

.filter-controls {
  width: 100%;
}

.filter-item {
  flex-shrink: 0;
}

.years-select {
  min-width: 170px;
}

@media (max-width: 599px) {
  .filter-toolbar {
    padding: 10px 12px;
  }

  .filter-controls {
    display: flex;
    flex-direction: column;
    align-items: stretch;
  }

  .filter-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
  }

  .years-select {
    min-width: 140px;
    flex-grow: 1;
  }
}
</style>

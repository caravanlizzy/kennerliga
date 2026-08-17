<template>
  <div class="q-mb-md filter-toolbar">
    <div class="filter-controls row items-center q-col-gutter-md">
      <!-- Player Count Filter -->
      <div class="filter-item row items-center q-gutter-x-sm">
        <div class="row items-center text-caption text-weight-bold text-grey-8 filter-label">
          <q-icon name="groups" size="18px" class="q-mr-xs text-primary" />
          <span>Players:</span>
        </div>
        <div class="player-btn-group row no-wrap items-center">
          <q-btn
            label="All"
            dense
            no-caps
            unelevated
            :color="selectedPlayerCounts.length === 0 ? 'primary' : 'white'"
            :text-color="selectedPlayerCounts.length === 0 ? 'white' : 'grey-8'"
            class="player-filter-btn"
            @click="togglePlayerCount('all')"
          />
          <q-btn
            label="2P"
            dense
            no-caps
            unelevated
            :color="selectedPlayerCounts.includes('2p') ? 'primary' : 'white'"
            :text-color="selectedPlayerCounts.includes('2p') ? 'white' : 'grey-8'"
            class="player-filter-btn"
            @click="togglePlayerCount('2p')"
          />
          <q-btn
            label="3P"
            dense
            no-caps
            unelevated
            :color="selectedPlayerCounts.includes('3p') ? 'primary' : 'white'"
            :text-color="selectedPlayerCounts.includes('3p') ? 'white' : 'grey-8'"
            class="player-filter-btn"
            @click="togglePlayerCount('3p')"
          />
          <q-btn
            label="4P"
            dense
            no-caps
            unelevated
            :color="selectedPlayerCounts.includes('4p') ? 'primary' : 'white'"
            :text-color="selectedPlayerCounts.includes('4p') ? 'white' : 'grey-8'"
            class="player-filter-btn"
            @click="togglePlayerCount('4p')"
          />
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
const selectedPlayerCounts = ref<string[]>([]);
const selectedYears = ref<number[]>([]);
const availableYears = ref<number[]>([]);
const loading = ref(false);

function togglePlayerCount(val: string) {
  if (val === 'all') {
    selectedPlayerCounts.value = [];
  } else {
    const idx = selectedPlayerCounts.value.indexOf(val);
    if (idx >= 0) {
      selectedPlayerCounts.value.splice(idx, 1);
    } else {
      selectedPlayerCounts.value.push(val);
    }
  }
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
    label: 'Most Played',
    field: (x: TUserDto) => x.most_participated_league_level,
    format: (val: number | null | undefined) =>
      val !== null && val !== undefined ? `L${val}` : '-',
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

.player-btn-group {
  border: 1px solid rgba(54, 64, 88, 0.15);
  border-radius: 20px;
  background: white;
  padding: 2px;
  overflow: hidden;
  box-shadow: none !important;
}

.player-filter-btn {
  border-radius: 16px;
  padding: 2px 10px;
  font-weight: 500;
  font-size: 0.82rem;
  box-shadow: none !important;
  transition: all 0.2s ease;
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

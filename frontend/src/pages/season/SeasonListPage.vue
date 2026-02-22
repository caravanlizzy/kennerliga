<template>
  <KennerTable
    v-if="!loading && !error && seasons && Array.isArray(seasons)"
    :create-button="isAdmin ? createBtn : undefined"
    flat
    title="Seasons"
    row-key="id"
    :rows="seasons"
    :columns="columns"
    @row-click="onRowClick"
  >
    <template v-slot:body-cell-details="props">
      <q-td :props="props">
        <div v-if="props.value.isEmpty">
          <q-icon name="group_off" color="grey-4" size="xs">
            <q-tooltip>No participants</q-tooltip>
          </q-icon>
        </div>
        <div v-else-if="props.value.isCompleted">
          <q-icon name="check_circle" color="positive" size="xs">
            <q-tooltip>Complete (all games selected and results reported)</q-tooltip>
          </q-icon>
        </div>
        <div v-else-if="props.value.isIncomplete">
          <q-icon name="pending" color="warning" size="xs">
            <q-tooltip>Incomplete (games or results missing)</q-tooltip>
          </q-icon>
        </div>
      </q-td>
    </template>

    <template v-slot:body-cell-actions="props">
      <q-td :props="props" class="q-gutter-x-sm">
        <KennerButton
          flat
          dense
          color="secondary"
          icon="visibility"
          label="View"
          :to="{ name: 'season-overview', params: { id: props.row.id } }"
          @click.stop
        />
        <KennerButton
          v-if="isAdmin"
          flat
          dense
          color="primary"
          icon="settings"
          label="Manage"
          :to="{ name: 'season-manage', params: { id: props.row.id } }"
          @click.stop
        />
      </q-td>
    </template>
  </KennerTable>

  <div v-else class="q-pa-md">
    <q-banner v-if="error" rounded dense class="q-mb-sm">
      <template #avatar><q-icon name="warning" color="negative" /></template>
      {{ error }}
    </q-banner>
    <q-skeleton v-else height="180px" square />
  </div>
</template>

<script setup lang="ts">
import KennerTable from 'components/tables/KennerTable.vue';
import { useAxios } from '@vueuse/integrations/useAxios';
import { api } from 'boot/axios';
import { useRouter } from 'vue-router';
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useUserStore } from 'stores/userStore';
import type { QTableProps } from 'quasar';
import type { TKennerButton, TSeasonDto } from 'src/types';
import KennerButton from 'src/components/base/KennerButton.vue';

type SeasonExtra = TSeasonDto & {
  is_empty?: boolean;
  is_incomplete?: boolean;
};

const userStore = useUserStore();
const { isAdmin } = storeToRefs(userStore);

// fetch seasons
const {
  data: seasons,
  isFinished,
  error: fetchError,
} = useAxios<SeasonExtra[]>('/season/seasons/', api);

const loading = computed(() => !isFinished.value);
const error = computed(() => fetchError.value?.message || null);

// status determination
const getSeasonStats = (s: SeasonExtra) => {
  return {
    isEmpty: s.is_empty,
    isCompleted: s.is_completed,
    isIncomplete: s.is_incomplete
  };
};

// navigation
const router = useRouter();
function onRowClick(_evt: unknown, row: SeasonExtra) {
  router.push({ name: 'season-overview', params: { id: row.id } });
}

// display helpers
const monthNames = ['', 'January','February','March','April','May','June','July','August','September','October','November','December'];
const monthLabel = (m?: number) => (m ? (monthNames[m] || `M${m}`) : 'Unknown');
const fallbackName = (s: SeasonExtra) => `${s.year} · S${s.month} (${monthLabel(s.month)})`;
const displayName  = (s: SeasonExtra) => s.name || fallbackName(s);

// columns for KennerTable
const columns = computed<QTableProps['columns']>(() => ([
  {
    name: 'details',
    label: '',
    align: 'center',
    field: (s: SeasonExtra) => getSeasonStats(s),
    style: 'width: 50px',
  },
  {
    name: 'name',
    label: 'Season',
    align: 'left',
    sortable: true,
    field: (s: SeasonExtra) => displayName(s),
    // render icon + name
    format: (val: string, row: SeasonExtra) => val, // keep value for filtering/sorting if KennerTable uses it
    headerStyle: 'white-space: nowrap',
    style: 'white-space: nowrap; max-width: 0',
  },
  {
    name: 'year',
    label: 'Year',
    field: 'year',
    align: 'left',
    sortable: true,
    headerStyle: 'white-space: nowrap',
  },
  {
    name: 'month',
    label: 'S',
    field: 'month',
    align: 'left',
    sortable: true,
    format: (v: number) => `S${v}`,
    headerStyle: 'white-space: nowrap',
  },
  {
    name: 'status',
    label: 'Status',
    field: 'status',
    align: 'left',
    sortable: true,
    headerStyle: 'white-space: nowrap',
  },
  {
    name: 'actions',
    label: 'Actions',
    align: 'right',
    headerStyle: 'white-space: nowrap',
  },
]));

// create button shown by KennerTable header
const createBtn: TKennerButton = {
  color: 'secondary',
  label: 'Season',
  icon: 'add_circle',
  forwardName: 'season-create', // if your KennerTable uses router push instead
};
</script>

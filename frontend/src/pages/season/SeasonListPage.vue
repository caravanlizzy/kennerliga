<template>
  <KennerTable
    v-if="!loading && !error && seasons && Array.isArray(seasons)"
    :create-button="createBtn"
    flat
    title="Seasons"
    row-key="id"
    :rows="seasons"
    :columns="columns"
    @row-click="onRowClick"
  />

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
import type { QTableProps } from 'quasar';
import type { TKennerButton } from 'src/types';

type Season = {
  id: number;
  year: number;
  month: number;
  name?: string;  // backend-provided if available
  status?: 'NEXT' | 'OPEN' | 'RUNNING' | 'DONE' | string;
};

// fetch seasons
const {
  data: seasons,
  isFinished,
  error: fetchError,
} = useAxios<Season[]>('/season/seasons/', api);

const loading = computed(() => !isFinished.value);
const error = computed(() => fetchError.value?.message || null);

// navigation
const router = useRouter();
function onRowClick(_evt: unknown, row: Season) {
  router.push({ name: 'season-detail', params: { id: row.id } });
}

// display helpers
const monthNames = ['', 'January','February','March','April','May','June','July','August','September','October','November','December'];
const monthLabel = (m?: number) => (m ? (monthNames[m] || `M${m}`) : 'Unknown');
const fallbackName = (s: Season) => `${s.year} · S${s.month} (${monthLabel(s.month)})`;
const displayName  = (s: Season) => s.name || fallbackName(s);

// columns for KennerTable
const columns = computed<QTableProps['columns']>(() => ([
  {
    name: 'name',
    label: 'Season',
    align: 'left',
    sortable: true,
    field: (s: Season) => displayName(s),
    // render icon + name
    format: (val: string, row: Season) => val, // keep value for filtering/sorting if KennerTable uses it
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
]));

// create button shown by KennerTable header
const createBtn: TKennerButton = {
  color: 'secondary',
  label: 'Season',
  icon: 'add_circle',
  forwardName: 'season-create', // if your KennerTable uses router push instead
};
</script>

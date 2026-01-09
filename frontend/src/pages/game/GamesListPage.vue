<template>
  <KennerTable
    v-if="!loading && !error && data && Array.isArray(data)"
    :create-button="button"
    flat
    title="Games"
    row-key="id"
    @row-click="onRowClick"
    :rows="data"
    :columns="columns"
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
import { TKennerButton } from 'src/types';
import { computed } from 'vue';

type GameRow = {
  id: number | string;
  name: string;
  platform: number | string; // id
  // ...any other fields your table needs
};

type Platform = { id: number | string; name: string };

// Fetch games
const {
  data,
  isFinished,
  error: gamesError,
} = useAxios<GameRow[]>('game/games', api);

// Fetch platforms
const {
  data: platformData,
  isFinished: isPlatformFinished,
  error: platformError,
} = useAxios<Platform[]>('game/platforms', api);

// Unified loading/error
const loading = computed(() => !isFinished.value || !isPlatformFinished.value);
const error = computed(() => gamesError?.value?.message || platformError?.value?.message || null);

// Build a map id->name from platformData (reactive, no manual watch needed)
const platformMap = computed<Record<string, string>>(() => {
  const arr = platformData.value ?? [];
  const map: Record<string, string> = {};
  for (const p of arr) {
    // coerce id to string to avoid 1 vs "1" mismatches
    map[String(p.id)] = p.name;
  }
  return map;
});

// Small helper to resolve platform label from a row
function lookupPlatform(row: GameRow) {
  return platformMap.value[String(row.platform)] ?? 'Unknown Platform';
}

// Router navigation
const router = useRouter();
function onRowClick(_evt: unknown, row: GameRow) {
  router.push({ name: 'game-detail', params: { id: row.id } });
}

// Create button
const button: TKennerButton = {
  color: 'secondary',
  label: 'Game',
  icon: 'add_circle',
  forwardName: 'game-create',
};

// Reactive columns
const columns = computed(() => [
  {
    name: 'game',
    label: 'Game',
    field: (x: GameRow) => x.name,
    align: 'left',
    sortable: true,
  },
  {
    name: 'platform',
    label: 'Platform',
    field: (x: GameRow) => lookupPlatform(x),
    align: 'left',
    sortable: true,
  },
]);
</script>

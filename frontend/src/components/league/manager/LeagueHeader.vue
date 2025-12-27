<template>
  <div
    class="row items-center q-mb-lg q-pa-md bg-grey-1 rounded-borders"
  >
    <div class="col-grow">
      <q-chip
        dense
        square
        color="grey-8"
        text-color="white"
        class="q-ml-xs text-weight-medium"
      >
        {{ season?.name }} · {{ season?.status }}
      </q-chip>
      <q-chip
        dense
        square
        color="primary"
        text-color="white"
        class="q-ml-xs text-weight-medium"
      >
        L {{ league?.level }}
      </q-chip>
    </div>
    <div class="col-auto">
      <q-btn
        flat
        icon="refresh"
        round
        color="secondary"
        size="md"
        @click="$emit('refresh')"
      >
        <q-tooltip>Refresh</q-tooltip>
      </q-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TSeasonDto } from 'src/types';

defineProps<{
  league: any;
  season: TSeasonDto | null;
}>();

defineEmits(['refresh']);
</script>

<template>
  <q-banner
    v-if="tieBreakerRequired"
    class="q-mb-md bg-warning text-dark"
    rounded
    dense
  >
    <template #avatar>
      <q-icon name="toll" />
    </template>
    <div class="text-body2">
      <template v-if="requiredTieBreaker?.name">
        <b>{{ requiredTieBreaker.name }}</b> needed for:
      </template>
      <template v-else> <b>Tie-breaker</b> needed for: </template>
      <span v-for="(grp, idx) in tieGroupDisplay" :key="grp.key">
        {{ grp.names.join(', ')
        }}<span v-if="idx < tieGroupDisplay.length - 1">; </span>
      </span>
    </div>
  </q-banner>
</template>

<script setup lang="ts">
import type { TTieBreakerDto } from 'src/types';

defineProps<{
  tieBreakerRequired: boolean;
  requiredTieBreaker?: TTieBreakerDto | null;
  tieGroupDisplay: Array<{ key: string; names: string[] }>;
}>();
</script>

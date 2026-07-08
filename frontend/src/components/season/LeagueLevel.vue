<template>
  <q-avatar
    v-if="!badge && !chip"
    :size="size"
    :font-size="fontSize"
    :color="getLeagueColor(Number(level))"
    text-color="white"
    class="text-weight-bold"
    v-bind="$attrs"
  >
    L{{ level }}
  </q-avatar>
  <q-badge
    v-else-if="badge"
    :color="getLeagueColor(Number(level))"
    class="text-weight-bold"
    v-bind="$attrs"
  >
    L{{ level }}
  </q-badge>
  <q-chip
    v-else-if="chip"
    :color="getLeagueColor(Number(level))"
    text-color="white"
    class="text-weight-bold"
    v-bind="$attrs"
  >
    L{{ level }}
  </q-chip>
</template>

<script setup lang="ts">
import { leagueColors } from 'src/composables/leagueColors';

defineOptions({
  inheritAttrs: false,
});

interface Props {
  level: number | string;
  badge?: boolean;
  chip?: boolean;
  size?: string;
  fontSize?: string;
}

withDefaults(defineProps<Props>(), {
  badge: false,
  chip: false,
  size: '48px',
  fontSize: '20px',
});

const { getLeagueColor } = leagueColors();
</script>

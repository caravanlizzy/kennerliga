<template>
  <q-avatar :size="size" class="flex flex-center text-white bg-red-4 text-bold">
    <span v-if="letters">{{ letters }}</span>
    <q-icon v-else name="person" size="70%" />

    <KennerTooltip>{{ displayUsername }}</KennerTooltip>
  </q-avatar>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';

const props = withDefaults(
  defineProps<{
    displayUsername: string;
    size?: string;
    maxLetters?: 1 | 2;
  }>(),
  {
    size: '28px',
    maxLetters: 2,
  }
);

const clean = computed(() => (props.displayUsername || '').trim());
const parts = computed(() => clean.value.split(/\s+/).filter(Boolean));

const letters = computed(() => {
  if (!clean.value) return '';
  if (props.maxLetters === 1) return clean.value[0].toUpperCase();
  if (parts.value.length >= 2) {
    return (parts.value[0][0] + parts.value.at(-1)![0]).toUpperCase();
  }
  return clean.value.slice(0, 2).toUpperCase();
});
</script>

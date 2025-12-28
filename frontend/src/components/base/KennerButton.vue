<template>
  <q-btn
    unelevated
    filled
    rounded
    :dense="isMobile"
    class="q-mx-xs"
    :color="color"
    :icon="icon"
    size="md"
    :label="label"
    v-bind="$attrs"
  >
    <slot></slot>
  </q-btn>
</template>

<script setup lang="ts">
import { useResponsive } from 'src/composables/responsive';
import { TKennerButton } from 'src/types';

withDefaults(defineProps<TKennerButton>(), {
  color: 'dark',
});
const { isMobile } = useResponsive();
</script>

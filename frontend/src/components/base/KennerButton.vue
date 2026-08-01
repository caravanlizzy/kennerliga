<template>
  <q-btn
    unelevated
    no-caps
    :rounded="shape === 'rounded'"
    :round="shape === 'circle'"
    :dense="isMobile"
    class="q-mx-xs"
    :class="{ 'squircle-shape': shape === 'squircle', 'square-shape': shape === 'square' || !shape }"
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
  shape: 'squircle',
});
const { isMobile } = useResponsive();
</script>

<style scoped>
.squircle-shape {
  border-radius: var(--kenner-card-radius, 0px) !important;
}
.square-shape {
  border-radius: 0px !important;
}
</style>

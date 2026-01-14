<template>
  <q-btn
    unelevated
    filled
    :rounded="shape === 'rounded' || !shape"
    :round="shape === 'circle'"
    :dense="isMobile"
    class="q-mx-xs"
    :class="{ 'squircle-shape': shape === 'squircle' }"
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
  shape: 'rounded',
});
const { isMobile } = useResponsive();
</script>

<style scoped>
.squircle-shape {
  border-radius: 12px !important;
}
</style>

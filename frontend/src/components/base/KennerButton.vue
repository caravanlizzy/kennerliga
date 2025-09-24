<template>
  <q-btn
    unelevated
    outline
    :dense="isMobile"
    class="q-mx-xs"
    :color="color"
    :icon="icon"
    size="md"
    :label="label"
  >
    <slot></slot>
  </q-btn>
</template>

<script setup lang="ts">
import { useResponsive } from 'src/composables/reponsive';
import { TKennerButton } from 'src/types';

withDefaults(defineProps<TKennerButton>(), {
  color: 'primary',
});
const { isMobile } = useResponsive();
</script>

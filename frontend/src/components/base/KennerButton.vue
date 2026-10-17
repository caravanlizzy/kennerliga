<template>
  <q-btn
    unelevated
    no-caps
    :to="computedTo"
    :rounded="isRounded"
    :round="isCircle"
    :dense="computedDense"
    class="q-mx-xs"
    :class="{
      'squircle-shape': isSquircle,
      'square-shape': isSquare,
    }"
    :color="color"
    :icon="icon"
    :size="size"
    :label="label"
    v-bind="$attrs"
  >
    <slot></slot>
  </q-btn>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useResponsive } from 'src/composables/responsive';
import { TKennerButton } from 'src/types';

const props = withDefaults(defineProps<TKennerButton>(), {
  color: 'dark',
  shape: 'squircle',
  size: 'md',
});
const { isMobile } = useResponsive();

const computedTo = computed(() => {
  if (props.to) return props.to;
  if (props.forwardName) {
    return { name: props.forwardName, params: props.forwardParams };
  }
  return undefined;
});

const isCircle = computed(() => props.shape === 'circle' || props.round);
const isRounded = computed(() => props.shape === 'rounded' || props.rounded);
const isSquare = computed(() => props.shape === 'square');
const isSquircle = computed(() => {
  if (isCircle.value || isRounded.value || isSquare.value) return false;
  return props.shape === 'squircle' || !props.shape;
});

const computedDense = computed(() =>
  props.dense !== undefined ? props.dense : isMobile.value
);
</script>

<style scoped>
.squircle-shape {
  border-radius: var(--kenner-card-radius, 12px) !important;
}
.square-shape {
  border-radius: 0px !important;
}
/* color="dark" (--q-dark) would vanish on dark surfaces */
.body--dark .q-btn.bg-dark {
  background: var(--kenner-surface-strong) !important;
}
</style>

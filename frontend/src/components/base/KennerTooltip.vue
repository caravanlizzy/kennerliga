<template>
  <q-tooltip
    class="kenner-tooltip"
    :delay="300"
    :hide-delay="0"
    anchor="top middle"
    self="bottom middle"
    transition-show="fade"
    transition-hide="fade"
    :offset="[0, 6]"
    :style="tooltipStyle"
  >
    <slot />
  </q-tooltip>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  color?: string
}>()

const tooltipStyle = computed(() => {
  if (!props.color) return {}
  return {
    borderColor: props.color,
  }
})
</script>

<style lang="scss">
.kenner-tooltip {
  background: #ffffff !important;
  color: #1f2329 !important;
  font-size: 12.5px;
  font-weight: 500;
  letter-spacing: 0.01em;
  line-height: 1.4;
  padding: 6px 10px !important;
  border-radius: 6px !important;
  border: 1px solid rgba(0, 0, 0, 0.12);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  white-space: nowrap;
  max-width: 280px;
}

body.body--dark .kenner-tooltip {
  background: #2a2f36 !important;
  color: #f5f5f5 !important;
  border-color: rgba(255, 255, 255, 0.14);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}
</style>


<template>
  <q-tooltip
    class="kenner-tooltip bg-white text-dark rounded-borders shadow-2 q-px-md q-py-sm text-caption"
    :delay="400"
    :hide-delay="100"
    anchor="top middle"
    self="bottom middle"
    transition-show="jump-up"
    transition-hide="fade"
    :offset="[10, 10]"
    :style="tooltipStyle"
  >
    <div class="column items-center justify-center">
      <slot />
    </div>
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
    border: `2px solid ${props.color}`,
  }
})
</script>

<style scoped lang="scss">
.kenner-tooltip {
  border: 1px solid rgba(0, 0, 0, 0.05);
  font-weight: 500;
  backdrop-filter: blur(4px);
  background: rgba(255, 255, 255, 0.95) !important;
}
</style>


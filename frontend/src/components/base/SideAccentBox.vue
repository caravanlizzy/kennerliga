<script setup lang="ts">
const props = withDefaults(
  defineProps<{ color?: string }>(),
  { color: 'primary' }
)

function resolveColor(c: string) {
  return ['primary', 'secondary', 'accent', 'dark', 'positive', 'negative', 'info', 'warning']
    .includes(c)
    ? `var(--q-${c})`
    : c
}
</script>

<template>
  <div
    class="bordered-container"
    :style="{ borderLeft: `4px solid ${resolveColor(props.color)}` }"
  >
    <slot />
  </div>
</template>

<style scoped>
.bordered-container {
  border-radius: 4px;    /* optional */
}
</style>

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
    class="bordered-container q-mt-md side-accent-border shadow-1"
    :style="{ borderLeft: `3px solid ${resolveColor(props.color)}` }"
  >
    <slot />
  </div>
</template>

<style scoped>
.side-accent-border {
  border-radius: 13px;
}

::v-deep(.q-card) {
  border-radius: 13px;
}
</style>



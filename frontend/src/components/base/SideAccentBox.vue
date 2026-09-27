
<template>
  <div
    class="q-mt-xs side-accent-border"
    :style="{
      borderLeft: `3px solid ${resolveColor(props.color)}`,
      borderTop: `1px solid ${resolveColor(props.color)}`,
      borderBottom: props.fullBorder
        ? `1px solid ${resolveColor(props.color)}`
        : '',
      borderRight: props.fullBorder
        ? `1px solid ${resolveColor(props.color)}`
        : '',
    }"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{ color?: string; fullBorder?: boolean }>(),
  { color: 'dark', fullBorder: true }
);

function resolveColor(c: string) {
  return [
    'dark',
    'secondary',
    'accent',
    'dark',
    'positive',
    'negative',
    'primary',
    'warning',
  ].includes(c)
    ? c === 'dark' ? 'var(--side-accent-dark)' : `var(--q-${c})`
    : c;
}
</script>

<style scoped>
.side-accent-border {
  --side-accent-dark: var(--q-dark);
}

.body--dark .side-accent-border {
  --side-accent-dark: var(--kenner-text-muted);
}
</style>


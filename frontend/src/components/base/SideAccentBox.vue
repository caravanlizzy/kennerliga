
<template>
  <div
    class="rounded-borders q-mt-xs side-accent-border"
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
    ? `var(--q-${c})`
    : c;
}
</script>


<template>
  <q-input
    hide-bottom-space
    :dark="dark"
    color="primary"
    v-model="modelValue"
    :label="label"
    lazy-rules
    :rules="rules"
    filled
    square
    v-bind="$attrs"
  >
    <template #prepend><slot name="prepend" /></template>
    <template #append><slot name="append" /></template>
    <template #before><slot name="before" /></template>
    <template #after><slot name="after" /></template>
    <template #hint><slot name="hint" /></template>
    <template #counter><slot name="counter" /></template>
  </q-input>
</template>

<script setup lang="ts">
type Rule = () => string
withDefaults(defineProps<{
  rules?: Rule[],
  label: string,
  dark?: boolean,
}>(), { dark: false });

const modelValue = defineModel();

</script>

<template>
  <q-select
    v-model="modelValue"
    v-bind="$attrs"
    :options="options"
    :label="label"
    square
    filled
    color="primary"
    class="rounded-borders"
  >
  </q-select>
</template>

<script setup lang="ts">
const modelValue = defineModel()

defineProps<{
  options: string[]
  label: string
}>()
</script>

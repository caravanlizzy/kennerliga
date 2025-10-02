<template>
  <q-select
    v-model="modelValue"
    :options="options"
    :label="label"
    square
    filled
    dense
    color="secondary"
    class="rounded-borders "
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

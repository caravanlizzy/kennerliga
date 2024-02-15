<template>
  <q-select filled color="secondary" :options="options" v-model="modelValue" :label="label" />
</template>

<script setup lang="ts">
const modelValue = defineModel()

defineProps<{
  options: string[],
  label: string,
}>()

</script>

<style scoped>

</style>

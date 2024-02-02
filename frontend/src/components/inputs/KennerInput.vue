<template>
  <q-input dark square outlined color="secondary" v-model="modelValue" :label="label" lazy-rules :rules="rules" />
</template>

<script setup lang="ts">
type Rule = () => string
defineProps<{
  rules: Rule[],
  label: string,
}>()

const modelValue = defineModel()

</script>

<style scoped>

</style>

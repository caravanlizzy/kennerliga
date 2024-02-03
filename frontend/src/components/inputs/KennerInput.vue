<template>
  <q-input :dark="dark" square outlined color="secondary" v-model="modelValue" :label="label" lazy-rules :rules="rules" />
</template>

<script setup lang="ts">
type Rule = () => string
withDefaults(defineProps<{
  rules: Rule[],
  label: string,
  dark?: boolean,
}>(), { dark: true });

const modelValue = defineModel();

</script>

<style scoped>

</style>

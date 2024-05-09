<template>
  <q-input hide-bottom-space  :dark="dark"  color="primary" v-model="modelValue" :label="label" lazy-rules :rules="rules" />
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

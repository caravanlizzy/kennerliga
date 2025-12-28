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
    <template v-for="(_, slot) in $slots" #[slot]="scope">
      <slot :name="slot" v-bind="scope || {}" />
    </template>
  </q-input>
</template>

<script setup lang="ts">
type Rule = () => string
withDefaults(defineProps<{
  rules?: any[],
  label?: string,
  dark?: boolean,
}>(), { dark: false });

const modelValue = defineModel();

</script>

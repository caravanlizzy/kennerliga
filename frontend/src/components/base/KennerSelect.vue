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
    <template v-for="(_, slot) in $slots" #[slot]="scope">
      <slot :name="slot" v-bind="scope || {}" />
    </template>
  </q-select>
</template>

<script setup lang="ts">
const modelValue = defineModel()

defineProps<{
  options: any[]
  label?: string
}>()
</script>

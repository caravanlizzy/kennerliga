<template>
  <div
    class="q-pa-xl flex flex-center column q-gutter-md"
  >
    <q-linear-progress v-if="$slots.skeleton" indeterminate class="q-mb-md" />
    <q-spinner-grid v-else size="4em" color="primary"/>

    <div class="text-subtitle1 text-dark">
      <span v-if="text"> {{text}}</span>
      <span v-else> Loading...</span>
    </div>

    <div v-if="$slots.skeleton" class="full-width q-mt-md">
      <slot name="skeleton" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ text?: string }>();
</script>

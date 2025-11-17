<template>
  <div
    class="q-pa-xl flex flex-center column q-gutter-md"
    style="min-height: 60vh"
  >
    <q-spinner-ios size="64px" color="primary" />
    <div class="text-subtitle1 text-primary">
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

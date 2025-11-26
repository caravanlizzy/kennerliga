<template>
  <div
    class="row items-center justify-between q-mb-sm bg-grey-4 q-pa-md rounded-borders"
  >
    <div>
      <slot />
    </div>
    <q-btn
      dense
      flat
      round
      icon="close"
      color="grey-8"
      size="md"
      @click="emit('onClose')"
    />
  </div>
</template>
<script setup lang="ts">
const emit = defineEmits(['onClose']);
</script>

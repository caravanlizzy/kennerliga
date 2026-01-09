<template>
  <div
    class="row items-center justify-between q-mb-sm bg-grey-4 q-pa-md rounded-borders"
  >
    <div>
      <slot />
    </div>
    <KennerButton
      dense
      flat
      round
      icon="cancel"
      color="grey-8"
      size="md"
      @click="emit('onClose')"
    />
  </div>
</template>
<script setup lang="ts">
import KennerButton from 'components/base/KennerButton.vue';
const emit = defineEmits(['onClose']);
</script>

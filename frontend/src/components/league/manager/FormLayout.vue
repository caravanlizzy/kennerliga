<template>
  <div
    class="q-pa-md q-mt-md bg-grey-1 rounded-borders col-12"
  >
    <FormHead @onClose="emit('onClose')" class="text-h6 text-weight-medium">
      <slot name="head"></slot>
    </FormHead>
    <div>
      <slot />
    </div>
  </div>
</template>
<script setup lang="ts">
import FormHead from 'components/league/manager/FormHead.vue';

const emit = defineEmits(['onClose']);
</script>

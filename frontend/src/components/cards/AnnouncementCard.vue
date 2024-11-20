<template>
  <div
    :class="`announcement bg-${background} q-px-lg q-py-md column ${
      props.type === 'NEUTRAL' ? 'text-primary' : 'text-white'
    }`"
  >
    <div class="text-bold">
      <slot name="title" />
    </div>
    <p class="">
      <slot name="content" />
    </p>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{ type: string }>();

const typeToBackgroundMap: { [key: string]: string } = {
  WINNER: 'secondary',
  INFO: 'primary',
  REGISTER: 'info',
  WARNING: 'negative',
  NEUTRAL: 'grey-2',
};

const typeToBorderMap: { [key: string]: string } = {
  WINNER: 'secondary',
  INFO: 'primary',
  REGISTER: 'info',
  WARNING: 'negative',
  NEUTRAL: 'grey-2',
}

const background = computed(() => {
  return typeToBackgroundMap[props.type];
});
</script>

<style scoped lang="scss">
.announcement {
  display: inline-flex;
  border-radius: 3px; /* Soft corners */
  text-align: center; /* Center the text */
  margin: auto;
}

.announcement p {
  margin: 0; /* Remove default paragraph margins */
}

</style>

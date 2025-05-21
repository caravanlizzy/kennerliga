<template>
  <div
    class="q-pa-md q-mb-sm full-width flex flex-center"
    :class="[
      `bg-${background}`,
      props.type === 'NEUTRAL' ? 'text-primary' : 'text-white',
      `border-top border-${border}`
    ]"
  >
    <div class="column items-center q-px-md q-mx-auto" style="max-width: 1200px; width: 100%">
      <div v-if="$slots.title" class="text-subtitle1 text-weight-medium q-mb-xs text-center">
        <slot name="title" />
      </div>
      <div v-if="$slots.content" class="text-body2 text-center">
        <slot name="content" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{ type: string }>();

const typeToBackgroundMap: Record<string, string> = {
  WINNER: 'secondary',
  INFO: 'primary',
  REGISTER: 'info',
  WARNING: 'negative',
  NEUTRAL: 'grey-2',
};

const typeToBorderMap: Record<string, string> = {
  WINNER: 'secondary',
  INFO: 'primary',
  REGISTER: 'info',
  WARNING: 'negative',
  NEUTRAL: 'grey-4',
};

const background = computed(() => typeToBackgroundMap[props.type] || 'grey-2');
const border = computed(() => typeToBorderMap[props.type] || 'grey-4');
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

<template>
  <div
    class=" q-my-xs"
    :style="{
      borderWidth: '3px',
      borderStyle: 'solid',
      borderImage: `linear-gradient(to right, var(--q-${color}) 0%, transparent 100%) 1`,
    }"
  >
    <q-expansion-item
      v-model="model"
      dense-toggle
      expand-separator
      expand-icon="expand_more"
      expanded-icon="expand_less"
      :expand-icon-class="`text-${color}`"
      :expanded-icon-class="`text-${color}`"
      :header-class="`text-${color} text-h5 q-py-xs justify-center with-opacity`"
    >
      <template #header>
        <div class="full-width row justify-center items-center">
          {{ title }}
        </div>
      </template>
      <q-separator :color="color"/>
      <div class="q-pa-md">
        <slot />
      </div>
    </q-expansion-item>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

// external (optional) model
const isOpened = defineModel<boolean>('isOpened');

// props
const props = withDefaults(
  defineProps<{
    title: string;
    color: string;
    defaultOpen?: boolean;
  }>(),
  {
    defaultOpen: true,
  }
);

// internal fallback state
const internal = ref<boolean>(props.defaultOpen);

// computed model that falls back to internal when external is absent
const model = computed({
  get: () => isOpened.value ?? internal.value,
  set: (v: boolean) => {
    if (isOpened.value === undefined) internal.value = v;
    else isOpened.value = v;
  },
});
</script>

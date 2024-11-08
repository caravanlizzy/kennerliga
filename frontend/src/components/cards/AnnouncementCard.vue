<template>
  <q-card square :class="`bg-${background} text-white`">
    <q-card-section class="">
      <div class="column text-h5">
        <div class="flex-center row">
          <slot name="title"/>
        </div>
      </div>
      <div class="column">
        <div class="flex-center row">
          <slot name="content"/>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>
<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{ type: string }>()

const typeToBackgroundMap: { [key: string]: string } = {
  WINNER: 'secondary',
  INFO: 'grey',
  REGISTER: 'accent',
  WARNING: 'negative',
  NEUTRAL: 'white',
};

const background = computed(() => {
  return typeToBackgroundMap[props.type];
});

</script>

<template>
  <div class="bg-black">
    <q-separator color="info" />
    <div class="q-px-md q-my-xs q-gutter-sm ">
      <q-breadcrumbs separator="-->" class="text-secondary" active-color="secondary">
        <template v-slot:separator>
          <q-icon
            aize="1.2em"
            name="arrow_right"
            color="secondary"
          />
        </template>
        <q-breadcrumbs-el v-for="segment in segments" :key="segment" :label="segment" icon="widgets" />
      </q-breadcrumbs>
    </div>
    <q-separator color="info" />
  </div>
</template>

<script setup lang="ts">

import { useRoute } from 'vue-router';
import { computed, ref, watch } from 'vue';

const route = useRoute();
const segments = ref(['home']);
watch(
  () => route.fullPath,
  () => {
    segments.value = ['home'];
    for (const part of route.fullPath.split('/')) {
      if(part !== ""){
        segments.value.push(part);
      }
    }
  }
)

</script>

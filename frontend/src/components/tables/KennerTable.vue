<template>
  <q-table table-header-class="text-info" flat :rows-per-page-options="[10, 20, 50]">
    <template v-if="createButton" v-slot:top-right>
      <KennerButton :color="createButton.color" :icon="createButton.icon" :label="createButton.label"
                     :to="{name: createButton.forwardName}" />
    </template>
  </q-table>
</template>


<script setup lang="ts">
import { TKennerButton } from 'src/types';
import KennerButton from 'components/base/KennerButton.vue';

defineProps<{
  createButton?: TKennerButton;
}>();
</script>

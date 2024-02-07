<template>
  <q-table card-class="bg-primary text-grey-3" table-header-class="text-info" dark flat :rows-per-page-options="[10, 20, 50]">
  <template v-if="createButton" v-slot:top-right>
    <kenner-button :color="createButton.color" :icon="createButton.icon" :label="createButton.label" :forward-name="createButton.forwardName" />
  </template>
  </q-table>
</template>


<script setup lang="ts">
import { TKennerButton } from 'components/models';
import KennerButton from 'components/buttons/KennerButton.vue';

defineProps<{
  createButton?: TKennerButton;
}>()
</script>

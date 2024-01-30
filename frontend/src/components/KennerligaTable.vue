<template>
  <q-table card-class="bg-primary text-grey-3" table-header-class="text-info" dark flat :rows-per-page-options="[10, 20, 50]">
  <template v-if="createButton" v-slot:top-right>
    <q-btn outline :color="createButton.color" :icon="createButton.icon" :label="createButton.label"/>
  </template>
  </q-table>
</template>


<script setup lang="ts">
import { CreateButton } from 'components/models';

defineProps<{
  createButton?: CreateButton;
}>()
</script>

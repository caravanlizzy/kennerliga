<template>
  <q-card flat class="table-wrapper">
    <q-table
      flat
      bordered
      :rows-per-page-options="[10, 20, 50]"
      table-header-class="text-primary text-weight-medium bg-grey-1"
      class="kenner-table"
      v-bind="$attrs"
    >
      <template v-if="createButton" v-slot:top-right>
        <KennerButton
          :color="createButton.color"
          :icon="createButton.icon"
          :label="createButton.label"
          :to="{ name: createButton.forwardName }"
          class="q-ml-sm"
        />
      </template>
    </q-table>
  </q-card>
</template>


<script setup lang="ts">
import { TKennerButton } from 'src/types';
import KennerButton from 'components/base/KennerButton.vue';

defineProps<{
  createButton?: TKennerButton;
}>();
</script>



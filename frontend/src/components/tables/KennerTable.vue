<template>
  <q-table
    flat
    :rows-per-page-options="[10, 20, 50]"
    table-header-class="text-dark text-weight-medium bg-grey-2"
    class="rounded-borders"
    table-class="text-grey-8"
  >
    <template v-if="createButton" v-slot:top-right>
      <KennerButton
        color="primary"
        icon="add"
        :label="createButton.label"
        :to="{ name: createButton.forwardName }"
        class="q-ml-sm"
      />
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

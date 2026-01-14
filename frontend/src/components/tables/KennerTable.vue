<template>
  <q-table
    flat
    :filter="filter"
    :rows-per-page-options="[20, 50, 0]"
    v-model:pagination="pagination"
    table-header-class="text-dark text-weight-medium bg-grey-2"
    class="rounded-borders"
    table-class="text-grey-8"
  >
    <template v-slot:top-left>
      <div v-if="title" class="text-h6 text-weight-bold">
        <template v-if="title.includes('KennerLiga')">
          {{ title.split('KennerLiga')[0] }}<span class="text-primary">Kenner</span><span class="text-accent">Liga</span>{{ title.split('KennerLiga')[1] }}
        </template>
        <template v-else>
          {{ title }}
        </template>
      </div>
    </template>
    <!-- forward ALL incoming slots (including scoped slots like body-cell-*) -->
    <template v-for="(_, slotName) in $slots" v-slot:[slotName]="slotProps">
      <slot :name="slotName" v-bind="slotProps" />
    </template>

    <template v-slot:no-data>
      <div class="full-width row flex-center q-pa-xl text-grey-5 italic">
        <q-icon name="sentiment_dissatisfied" size="32px" class="q-mr-sm" />
        No entries found.
      </div>
    </template>

    <template v-slot:top-right>
      <div class="row q-gutter-sm no-wrap">
        <KennerInput
          v-model="filter"
          placeholder="Search..."
          debounce="300"
          style="min-width: 250px"
        >
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </KennerInput>

        <KennerButton
          v-if="createButton"
          color="primary"
          icon="add"
          :label="createButton.label"
          :to="{ name: createButton.forwardName }"
        />
      </div>
    </template>
  </q-table>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { TKennerButton } from 'src/types';
import KennerButton from 'components/base/KennerButton.vue';
import KennerInput from 'components/base/KennerInput.vue';

defineProps<{
  title?: string;
  createButton?: TKennerButton;
}>();

const filter = ref('');
const pagination = ref({
  rowsPerPage: 0,
});
</script>

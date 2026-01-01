<template>
  <q-table
    flat
    :title="title"
    :filter="filter"
    :rows-per-page-options="[20, 50, 0]"
    v-model:pagination="pagination"
    table-header-class="text-dark text-weight-medium bg-grey-2"
    class="rounded-borders"
    table-class="text-grey-8"
  >
    <!-- forward ALL incoming slots (including scoped slots like body-cell-*) -->
    <template v-for="(_, slotName) in $slots" v-slot:[slotName]="slotProps">
      <slot :name="slotName" v-bind="slotProps" />
    </template>

    <template v-slot:no-data>
      <!-- hide default "No data available" -->
    </template>

    <template v-slot:top-right>
      <div class="row q-gutter-sm no-wrap">
        <KennerInput
          v-model="filter"
          placeholder="Search..."
          debounce="300"
          outlined
          dense
          class="bg-white"
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

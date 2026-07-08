<template>
  <q-table
    flat
    :filter="filter"
    :rows-per-page-options="[20, 50, 0]"
    v-model:pagination="pagination"
    table-header-class="kenner-table__header-row"
    class="kenner-table"
    table-class="kenner-table__body"
  >
    <template v-slot:top-left>
      <div v-if="title" class="row items-center no-wrap kenner-table__title-wrap">
        <template v-if="title.includes('KennerLiga')">
          <span v-if="title.split('KennerLiga')[0].trim()" class="text-h6 text-weight-bolder kenner-table__title q-mr-sm">{{ title.split('KennerLiga')[0] }}</span>
          <BrandLogo icon-size="32px" word-size="1.25rem" />
          <span v-if="title.split('KennerLiga')[1].trim()" class="text-h6 text-weight-bolder kenner-table__title q-ml-sm">{{ title.split('KennerLiga')[1] }}</span>
        </template>
        <template v-else>
          <span class="text-h6 text-weight-bolder kenner-table__title">{{ title }}</span>
        </template>
      </div>
    </template>
    <!-- forward ALL incoming slots (including scoped slots like body-cell-*) -->
    <template v-for="(_, slotName) in $slots" v-slot:[slotName]="slotProps">
      <slot :name="slotName" v-bind="slotProps" />
    </template>

    <template v-slot:no-data>
      <div class="full-width row flex-center q-pa-xl text-grey-6 italic">
        <q-icon name="sentiment_dissatisfied" size="28px" class="q-mr-sm" />
        No entries found.
      </div>
    </template>

    <template v-slot:top-right>
      <div class="row q-gutter-sm no-wrap items-center">
        <KennerInput
          v-model="filter"
          placeholder="Search..."
          debounce="300"
          class="kenner-table__search"
          style="min-width: 240px"
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
import BrandLogo from 'components/base/BrandLogo.vue';

defineProps<{
  title?: string;
  createButton?: TKennerButton;
}>();

const filter = ref('');
const pagination = ref({
  rowsPerPage: 0,
});
</script>

<style scoped lang="scss">
.kenner-table {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(54, 64, 88, 0.08);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(54, 64, 88, 0.04);
  overflow: hidden;
}

.kenner-table__title {
  color: #1f2937;
  letter-spacing: -0.3px;
}

:deep(.q-table__top) {
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.6) 0%, rgba(255, 255, 255, 0.15) 100%);
  border-bottom: 1px solid rgba(54, 64, 88, 0.06);
}

:deep(.kenner-table__header-row th) {
  background: transparent;
  color: #64748b;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  border-bottom: 1px solid rgba(54, 64, 88, 0.08);
  padding: 12px 16px;
}

:deep(.kenner-table__body) {
  color: #334155;
}

:deep(.q-table tbody td) {
  font-size: 13.5px;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(54, 64, 88, 0.05);
}

:deep(.q-table tbody tr) {
  transition: background 0.18s ease;
}

:deep(.q-table tbody tr:hover) {
  background: rgba(99, 102, 241, 0.04);
}

:deep(.q-table tbody tr:last-child td) {
  border-bottom: none;
}

:deep(.q-table__bottom) {
  border-top: 1px solid rgba(54, 64, 88, 0.06);
  color: #64748b;
  font-size: 12px;
  padding: 8px 16px;
  min-height: 44px;
}

.kenner-table__search :deep(.q-field__control) {
  border-radius: 999px;
}

</style>

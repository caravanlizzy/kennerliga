<template>
  <q-table
    flat
    :filter="filter"
    :rows-per-page-options="rowsPerPageOptions || [10, 20, 50, 0]"
    v-model:pagination="paginationModel"
    table-header-class="kenner-table__header-row"
    class="kenner-table"
    table-class="kenner-table__body"
  >
    <template v-slot:top-left>
      <div
        v-if="title"
        class="row items-center no-wrap kenner-table__title-wrap"
      >
        <template v-if="title.includes('KennerLiga')">
          <span
            v-if="title.split('KennerLiga')[0].trim()"
            class="text-h6 text-weight-bolder kenner-table__title q-mr-sm"
            >{{ title.split('KennerLiga')[0] }}</span
          >
          <BrandLogo icon-size="32px" word-size="1.25rem" />
          <span
            v-if="title.split('KennerLiga')[1].trim()"
            class="text-h6 text-weight-bolder kenner-table__title q-ml-sm"
            >{{ title.split('KennerLiga')[1] }}</span
          >
        </template>
        <template v-else>
          <span class="text-h6 text-weight-bolder kenner-table__title">{{
            title
          }}</span>
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
      <div class="row q-gutter-sm items-center kenner-table__actions">
        <KennerInput
          v-model="filter"
          placeholder="Search..."
          debounce="300"
          class="kenner-table__search"
        >
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </KennerInput>

        <KennerButton
          v-if="createButton"
          color="primary"
          icon="add"
          outline
          :label="createButton.label"
          :to="{ name: createButton.forwardName }"
          class="kenner-table__create-btn"
        />
      </div>
    </template>
  </q-table>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import type { QTableProps } from 'quasar';
import { TKennerButton } from 'src/types';
import KennerButton from 'components/base/KennerButton.vue';
import KennerInput from 'components/base/KennerInput.vue';
import BrandLogo from 'components/base/BrandLogo.vue';

const props = withDefaults(
  defineProps<{
    title?: string;
    createButton?: TKennerButton;
    pagination?: QTableProps['pagination'];
    rowsPerPageOptions?: number[];
  }>(),
  {
    rowsPerPageOptions: () => [10, 20, 50, 0],
  }
);

const emit = defineEmits<{
  (e: 'update:pagination', value: QTableProps['pagination']): void;
}>();

const filter = ref('');
const paginationModel = ref<NonNullable<QTableProps['pagination']>>({
  rowsPerPage: 20,
  ...(props.pagination || {}),
});

watch(
  () => props.pagination,
  (newVal) => {
    if (newVal) {
      paginationModel.value = { ...paginationModel.value, ...newVal };
    }
  },
  { deep: true }
);

watch(
  paginationModel,
  (newVal) => {
    emit('update:pagination', newVal);
  },
  { deep: true }
);
</script>

<style scoped lang="scss">
.kenner-table {
  background: var(--kenner-bg-glass-card);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--kenner-border-color);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(54, 64, 88, 0.04);
  overflow: hidden;
}

.kenner-table__title {
  color: var(--kenner-text-color);
  letter-spacing: -0.3px;
}

:deep(.q-table__top) {
  padding: 16px 20px;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.6) 0%,
    rgba(255, 255, 255, 0.15) 100%
  );
  border-bottom: 1px solid var(--kenner-border-color);
}

:deep(.kenner-table__header-row th) {
  background: transparent;
  color: var(--kenner-text-muted);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  border-bottom: 1px solid var(--kenner-border-color);
  padding: 12px 16px;
}

:deep(.kenner-table__body) {
  color: #334155;
}

:deep(.q-table tbody td) {
  font-size: 13.5px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--kenner-border-subtle);
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
  border-top: 1px solid var(--kenner-border-color);
  color: var(--kenner-text-muted);
  font-size: 12px;
  padding: 8px 16px;
  min-height: 44px;
}

:deep(.q-table__middle) {
  -webkit-overflow-scrolling: touch;
  touch-action: pan-x pan-y;
  overscroll-behavior-x: contain;
}

.kenner-table__actions {
  width: auto;
  flex-wrap: nowrap;
}

.kenner-table__search {
  min-width: 240px;
}

.kenner-table__search :deep(.q-field__control) {
  border-radius: 999px;
}

@media (max-width: 599px) {
  :deep(.q-table__top) {
    padding: 10px 12px;
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .kenner-table__title-wrap {
    width: 100%;
    margin-bottom: 2px;
  }

  .kenner-table__actions {
    width: 100%;
    flex-wrap: nowrap;
    gap: 8px;
  }

  .kenner-table__search {
    min-width: 0;
    flex: 1 1 auto;
    width: 100%;
  }

  .kenner-table__create-btn {
    flex-shrink: 0;
  }
}

// Dark: translucent white header wash and slate body text don't fit tokens
.body--dark .kenner-table {
  :deep(.q-table__top) {
    background: linear-gradient(
      135deg,
      rgba(255, 255, 255, 0.06) 0%,
      rgba(255, 255, 255, 0.02) 100%
    );
  }

  :deep(.kenner-table__body) {
    color: var(--kenner-text-secondary);
  }

  :deep(.q-table tbody tr:hover) {
    background: var(--kenner-hover-bg);
  }
}
</style>

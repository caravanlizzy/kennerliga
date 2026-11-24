<template>
  <div
    class="kenner-player-filter row items-center no-wrap"
    :class="{
      'kenner-player-filter--mobile': isMobile,
      'kenner-player-filter--dense': dense,
    }"
  >
    <!-- Label & Icon Section -->
    <div
      v-if="label || icon"
      class="kenner-player-filter__label row items-center no-wrap text-caption text-weight-bold q-mr-xs"
      :class="isMobile ? 'q-mr-xs' : 'q-mr-sm'"
    >
      <q-icon
        v-if="icon"
        :name="icon"
        :size="isMobile || dense ? '16px' : '18px'"
        color="primary"
        class="q-mr-xs"
      />
      <span v-if="label && !isMobile" class="text-grey-8">{{ label }}</span>
    </div>

    <!-- Segmented Button Track -->
    <div
      class="kenner-player-filter__track row items-center no-wrap"
      role="group"
      aria-label="Player count filters"
    >
      <!-- "All" Segment -->
      <button
        type="button"
        class="kenner-player-filter__btn"
        :class="{
          'kenner-player-filter__btn--active': isAllSelected,
        }"
        @click="selectAll"
      >
        <span>All</span>
      </button>

      <!-- Individual Count Segments -->
      <button
        v-for="pc in availableCounts"
        :key="pc"
        type="button"
        class="kenner-player-filter__btn"
        :class="{
          'kenner-player-filter__btn--active': isCountSelected(pc),
        }"
        @click="toggleCount(pc)"
      >
        <span>{{ formatCountLabel(pc) }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useResponsive } from 'src/composables/responsive';

const props = withDefaults(
  defineProps<{
    modelValue: string[];
    availableCounts?: string[];
    label?: string;
    icon?: string;
    dense?: boolean;
  }>(),
  {
    availableCounts: () => ['2p', '3p', '4p'],
    icon: 'groups',
    dense: false,
  }
);

const emit = defineEmits<{
  (e: 'update:modelValue', value: string[]): void;
  (e: 'change', value: string[]): void;
}>();

const { isMobile } = useResponsive();

const isAllSelected = computed(
  () => !props.modelValue || props.modelValue.length === 0
);

function isCountSelected(pc: string): boolean {
  if (isAllSelected.value) return false;
  return props.modelValue.includes(pc.toLowerCase());
}

function formatCountLabel(pc: string): string {
  return pc.trim().toUpperCase();
}

function selectAll() {
  emit('update:modelValue', []);
  emit('change', []);
}

function toggleCount(pc: string) {
  const normalized = pc.toLowerCase();
  const current = props.modelValue ? [...props.modelValue] : [];
  const idx = current.indexOf(normalized);

  if (idx >= 0) {
    current.splice(idx, 1);
  } else {
    current.push(normalized);
  }

  // If all available options are selected or none remain, collapse to "All" (empty array)
  if (
    current.length === 0 ||
    current.length === props.availableCounts.length
  ) {
    emit('update:modelValue', []);
    emit('change', []);
  } else {
    emit('update:modelValue', current);
    emit('change', current);
  }
}
</script>

<style scoped lang="scss">
.kenner-player-filter {
  display: inline-flex;
  align-items: center;

  &__label {
    user-select: none;
    line-height: 1;
    color: var(--kenner-text-secondary, #475569);
  }

  &__track {
    background: var(--kenner-surface-muted, #f1f5f9);
    border: 1px solid var(--kenner-border-subtle, rgba(0, 0, 0, 0.08));
    border-radius: 10px;
    padding: 3px;
    gap: 3px;
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.04);
  }

  &__btn {
    appearance: none;
    background: transparent;
    border: none;
    outline: none;
    cursor: pointer;
    border-radius: 7px;
    padding: 4px 10px;
    font-size: 0.78rem;
    font-weight: 600;
    line-height: 1.2;
    color: var(--kenner-text-secondary, #64748b);
    transition: all 0.16s cubic-bezier(0.4, 0, 0.2, 1);
    user-select: none;
    white-space: nowrap;

    &:hover:not(&--active) {
      background: var(--kenner-hover-bg, rgba(0, 0, 0, 0.05));
      color: var(--kenner-text-strong, #0f172a);
    }

    &--active {
      background: var(--q-primary, #1976d2);
      color: #ffffff;
      font-weight: 700;
      box-shadow: 0 1px 3px rgba(25, 118, 210, 0.35);

      &:hover {
        filter: brightness(1.05);
      }
    }
  }

  &--mobile,
  &--dense {
    .kenner-player-filter__track {
      padding: 2px;
      gap: 2px;
      border-radius: 8px;
    }

    .kenner-player-filter__btn {
      padding: 3px 8px;
      font-size: 0.72rem;
      border-radius: 6px;
    }
  }
}

.body--dark {
  .kenner-player-filter__label span {
    color: var(--kenner-text-secondary, #cbd5e1);
  }

  .kenner-player-filter__track {
    background: var(--kenner-surface-strong, #2d2d38);
    border-color: var(--kenner-border-color, rgba(255, 255, 255, 0.1));
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.2);
  }

  .kenner-player-filter__btn {
    color: var(--kenner-text-secondary, #94a3b8);

    &:hover:not(.kenner-player-filter__btn--active) {
      background: rgba(255, 255, 255, 0.08);
      color: #ffffff;
    }

    &--active {
      background: var(--q-primary, #1976d2);
      color: #ffffff;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.4);
    }
  }
}
</style>

<template>
  <div
    :id="sectionId"
    class="q-mt-xl content-section-container relative-position q-pa-lg"
    :class="`indicator-${color}`"
  >
    <div
      class="section-watermark absolute-top-right q-ma-md"
      :class="`text-${color}`"
      style="opacity: 0.04; pointer-events: none; transform: rotate(-15deg)"
    >
      <q-icon :name="icon" size="140px" />
    </div>


    <template v-if="expandable">
      <q-expansion-item
        v-model="isOpened"
        dense-toggle
        expand-separator
        expand-icon="expand_more"
        expanded-icon="expand_less"
        :expand-icon-class="`text-${color}`"
        :expanded-icon-class="`text-${color}`"
        header-class="section-header relative-position"
      >
        <template #header>
          <div class="full-width row items-center no-wrap">
            <slot name="title">
              <span class="text-h5 text-weight-bold tracking-tight" :class="`text-${color}`">{{ title }}</span>
            </slot>
            <slot name="header-extra" />
            <q-space />
          </div>
        </template>
        <div class="section-content relative-position q-pt-md">
          <slot />
        </div>
      </q-expansion-item>
    </template>
    <template v-else>
      <div
        class="section-header full-width row items-center no-wrap relative-position"
      >
        <slot name="title">
          <span class="text-h5 text-weight-bold tracking-tight" :class="`text-${color}`">{{ title }}</span>
        </slot>
        <slot name="header-extra" />
        <q-space />
      </div>
      <div class="section-content relative-position q-pt-md">
        <slot />
      </div>
    </template>
  </div>
  </template>

  <script setup lang="ts">
  import { computed, onMounted, onUnmounted } from 'vue';
  import { useUiStore } from 'src/stores/uiStore';

  const uiStore = useUiStore();

  const isOpened = defineModel<boolean>('isOpened', { default: true });

  const props = withDefaults(
    defineProps<{
      id?: string;
      title: string;
      color: string;
      icon?: string;
      titleEnd?: boolean;
      expandable?: boolean;
    }>(),
    {
      titleEnd: false,
      expandable: false,
      icon: 'article'
    }
  );

  const sectionId = computed(() => props.id || props.title.toLowerCase().replace(/\s+/g, '-'));

  const register = () => {
    uiStore.registerSection({
      id: sectionId.value,
      title: props.title,
      icon: props.icon || 'article',
      color: props.color
    });
  };

  onMounted(register);

  onUnmounted(() => {
    uiStore.unregisterSection(sectionId.value);
  });
  </script>

  <style scoped lang="scss">
  .content-section-container {
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
    position: relative;
    background: white;
    border-radius: 16px;
    border: 1px solid rgba(0, 0, 0, 0.08);
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
    overflow: hidden;

    &:hover {
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    }

    &.indicator-primary { border-top: 4px solid var(--q-primary); --separator-color: var(--q-primary); }
    &.indicator-secondary { border-top: 4px solid var(--q-secondary); --separator-color: var(--q-secondary); }
    &.indicator-accent { border-top: 4px solid var(--q-accent); --separator-color: var(--q-accent); }
    &.indicator-dark { border-top: 4px solid var(--q-dark); --separator-color: var(--q-dark); }
    &.indicator-info { border-top: 4px solid var(--q-info); --separator-color: var(--q-info); }
    &.indicator-warning { border-top: 4px solid var(--q-warning); --separator-color: var(--q-warning); }
    &.indicator-negative { border-top: 4px solid var(--q-negative); --separator-color: var(--q-negative); }
    &.indicator-positive { border-top: 4px solid var(--q-positive); --separator-color: var(--q-positive); }
  }

  .section-header {
    padding: 0 0 12px 0;
    border-bottom: 1px solid color-mix(in srgb, var(--separator-color, black) 12%, transparent);

    :deep(.q-item) {
      padding: 0;
      min-height: unset;
    }
  }

  .section-content {
    z-index: 1;
  }

  .section-watermark {
    z-index: 0;
    transition: all 0.3s ease;
    pointer-events: none;
  }

  .content-section-container:hover .section-watermark {
    opacity: 0.08 !important;
    transform: rotate(-10deg) scale(1.1) !important;
  }
  </style>

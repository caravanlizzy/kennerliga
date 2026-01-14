<template>
  <div
    :id="sectionId"
    class="q-mt-xl content-section-container relative-position"
    :class="`indicator-${color}`"
  >
    <!-- Background Watermark -->
    <div
      class="section-watermark absolute-top-right q-ma-md"
      :class="`text-${color}`"
      style="opacity: 0.03; pointer-events: none; transform: rotate(-15deg)"
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
            <q-icon :name="icon" class="q-mr-sm" size="sm" style="opacity: 0.7" />
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
        <q-icon :name="icon" class="q-mr-sm" size="sm" style="opacity: 0.7; color: var(--q-primary)" :class="`text-${color}`" />
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
  import { computed, onMounted, onUnmounted, onActivated } from 'vue';
  import { useUiStore } from 'src/stores/uiStore';
  import { useResponsive } from 'src/composables/responsive';

  const uiStore = useUiStore();
  const { isMobile } = useResponsive();

  const isOpened = defineModel<boolean>('isOpened', { default: true });

  const props = withDefaults(
    defineProps<{
      id?: string;
      title: string;
      color: string;
      icon?: string;
      bordered?: boolean;
      titleEnd?: boolean;
      expandable?: boolean;
    }>(),
    {
      titleEnd: false,
      expandable: false,
      bordered: true,
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
  onActivated(register);

  onUnmounted(() => {
    uiStore.unregisterSection(sectionId.value);
  });
  </script>

  <style scoped lang="scss">
  .content-section-container {
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
    padding-left: 16px;
    position: relative;

    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 8px;
      bottom: 0;
      width: 3px;
      border-radius: 4px;
      background: currentColor;
      opacity: 0.3;
      z-index: 1;
    }

    &.indicator-primary::before { background: var(--q-primary); opacity: 0.6; }
    &.indicator-secondary::before { background: var(--q-secondary); opacity: 0.6; }
    &.indicator-accent::before { background: var(--q-accent); opacity: 0.6; }
    &.indicator-dark::before { background: var(--q-dark); opacity: 0.6; }
    &.indicator-info::before { background: var(--q-info); opacity: 0.6; }
    &.indicator-warning::before { background: var(--q-warning); opacity: 0.6; }
    &.indicator-negative::before { background: var(--q-negative); opacity: 0.6; }
    &.indicator-positive::before { background: var(--q-positive); opacity: 0.6; }
  }

  .section-header {
    padding: 8px 0;
    border-bottom: 1px solid rgba(54, 64, 88, 0.08);
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

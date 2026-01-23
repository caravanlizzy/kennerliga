<template>
  <div
    :id="sectionId"
    class="q-mt-xl content-section-container relative-position"
    :class="`indicator-${color}`"
  >
    <!-- Background Watermark -->
    <div
      v-if="false"
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

  onUnmounted(() => {
    uiStore.unregisterSection(sectionId.value);
  });
  </script>

  <style scoped lang="scss">
  .content-section-container {
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
    position: relative;

    &.indicator-primary { border-top: 2px solid var(--q-primary); }
    &.indicator-secondary { border-top: 2px solid var(--q-secondary); }
    &.indicator-accent { border-top: 2px solid var(--q-accent); }
    &.indicator-dark { border-top: 2px solid var(--q-dark); }
    &.indicator-info { border-top: 2px solid var(--q-info); }
    &.indicator-warning { border-top: 2px solid var(--q-warning); }
    &.indicator-negative { border-top: 2px solid var(--q-negative); }
    &.indicator-positive { border-top: 2px solid var(--q-positive); }
  }

  .section-header {
    padding: 12px 0 8px 0;
    border-bottom: 1px solid rgba(54, 64, 88, 0.04);
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

<template>
  <div
    :id="sectionId"
    class="content-section-container relative-position"
    :class="[
      `indicator-${color}`,
      isMobile ? 'q-pa-md no-border-radius-mobile' : 'q-pa-lg',
      { 'q-mt-xl': !noMargin, 'content-section--flat': flat }
    ]"
  >
    <div
      class="section-watermark absolute-top-right q-ma-md"
      :class="`text-${color}`"
      style="opacity: 0.03; pointer-events: none; transform: rotate(-15deg)"
    >
      <q-icon :name="icon" size="120px" />
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
      titleEnd?: boolean;
      expandable?: boolean;
      flat?: boolean;
      noMargin?: boolean;
    }>(),
    {
      titleEnd: false,
      expandable: false,
      icon: 'article',
      flat: false,
      noMargin: false
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
  position: relative;
  background: white;
  border-radius: var(--kenner-card-radius, 0px);
  border: 1px solid var(--kenner-border-color);
  box-shadow: var(--kenner-card-shadow);
  overflow: hidden;

  &.content-section--flat {
      border: none !important;
      box-shadow: none !important;
      background: transparent !important;
      border-radius: 0 !important;
      padding-left: 0 !important;
      padding-right: 0 !important;
      padding-top: 32px !important;
      padding-bottom: 32px !important;
  
      @media (max-width: 599px) {
        padding-top: 24px !important;
        padding-bottom: 24px !important;
      }

    &::before {
      display: none;
    }

    .section-header {
      padding-top: 0;
    }
  }

  // Sharp accent top stripe
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--accent-color);
    pointer-events: none;
    z-index: 2;
  }

  &.indicator-primary { --separator-color: var(--q-primary); --accent-color: var(--q-primary); }
  &.indicator-secondary { --separator-color: var(--q-secondary); --accent-color: var(--q-secondary); }
  &.indicator-accent { --separator-color: var(--q-accent); --accent-color: var(--q-accent); }
  &.indicator-dark { --separator-color: var(--q-dark); --accent-color: var(--q-dark); }
  &.indicator-info { --separator-color: var(--q-info); --accent-color: var(--q-info); }
  &.indicator-warning { --separator-color: var(--q-warning); --accent-color: var(--q-warning); }
  &.indicator-negative { --separator-color: var(--q-negative); --accent-color: var(--q-negative); }
  &.indicator-positive { --separator-color: var(--q-positive); --accent-color: var(--q-positive); }
}

  .section-header {
    padding: 0 0 10px 0;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);

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
    pointer-events: none;
  }
  </style>

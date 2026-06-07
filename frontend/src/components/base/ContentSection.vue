<template>
  <div
    :id="sectionId"
    class="q-mt-xl content-section-container relative-position q-pa-lg"
    :class="`indicator-${color}`"
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
  position: relative;
  background: white;
  border-radius: 10px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05);
  overflow: hidden;

  // Subtle accent top stripe (thinner / softer than the original)
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--accent-color);
    opacity: 0.55;
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

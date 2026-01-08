<template>
  <div
    v-if="!isMinimized"
    class="q-mt-xl content-section-container relative-position"
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
            <div :class="`bg-${color}`" class="header-indicator q-mr-md" />
            <q-icon :name="icon" class="q-mr-sm" size="sm" style="opacity: 0.7" />
            <slot name="title">
              <span class="text-h5 text-weight-bold tracking-tight" :class="`text-${color}`">{{ title }}</span>
            </slot>
            <slot name="header-extra" />
            <q-btn
              v-if="minimizable && !isMobile"
              flat
              round
              dense
              icon="close"
              size="sm"
              class="minimize-btn absolute-top-right q-ma-xs fancy-close-btn"
              @click.stop="minimize"
              style="z-index: 2"
            >
              <q-tooltip>Minimize</q-tooltip>
            </q-btn>
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
        <div :class="`bg-${color}`" class="header-indicator q-mr-md" />
        <q-icon :name="icon" class="q-mr-sm" size="sm" style="opacity: 0.7; color: var(--q-primary)" :class="`text-${color}`" />
        <slot name="title">
          <span class="text-h5 text-weight-bold tracking-tight" :class="`text-${color}`">{{ title }}</span>
        </slot>
        <slot name="header-extra" />
        <q-btn
          v-if="minimizable && !isMobile"
          flat
          round
          dense
          icon="close"
          size="sm"
          class="minimize-btn absolute-top-right q-ma-xs fancy-close-btn"
          @click="minimize"
          style="z-index: 2"
        >
          <q-tooltip>Minimize</q-tooltip>
        </q-btn>
      </div>
      <div class="section-content relative-position q-pt-md">
        <slot />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
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
    minimizable?: boolean;
  }>(),
  {
    titleEnd: false,
    expandable: false,
    bordered: true,
    minimizable: false,
    icon: 'article'
  }
);

const sectionId = computed(() => props.id || props.title || 'default-section');
const isMinimized = computed(() => uiStore.isMinimized(sectionId.value));

function minimize() {
  uiStore.minimize({
    id: sectionId.value,
    title: props.title,
    icon: props.icon,
    color: props.color,
    type: 'section'
  });
}
</script>

<style scoped lang="scss">
.content-section-container {
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.section-header {
  padding: 8px 0;
  border-bottom: 1px solid rgba(54, 64, 88, 0.08);
}

.header-indicator {
  width: 4px;
  height: 24px;
  border-radius: 4px;
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

.fancy-close-btn {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  opacity: 0.8;
  background: rgba(0, 0, 0, 0.05);
  color: var(--q-primary);
  font-weight: bold;

  &:hover {
    opacity: 1;
    background: rgba(0, 0, 0, 0.12);
    transform: rotate(90deg) scale(1.15);
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
  }
}
</style>

<template>
  <div
    v-if="!isMinimized"
    :class="[
      bordered ? `border-2 rounded-borders border-${color}` : '',
      { 'section-gradient': !bordered, 'bg-white': bordered }
    ]"
    class="q-mt-md content-section-container rounded-borders shadow-subtle border-subtle relative-position"
  >
    <!-- Background Watermark -->
    <div
      class="section-watermark absolute-bottom-right q-ma-md"
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
        :header-class="`text-${color} text-h5 q-py-sm justify-center header-tint relative-position`"
      >
        <template #header>
          <div class="full-width row justify-center items-center">
            <q-icon :name="icon" class="q-mr-sm" size="sm" style="opacity: 0.7" />
            <slot name="title">
              <span class="text-weight-bold">{{ title }}</span>
            </slot>
            <slot name="header-extra" />
            <q-btn
              v-if="minimizable && !isMobile"
              flat
              round
              dense
              icon="close"
              size="sm"
              class="minimize-btn absolute-top-right q-ma-xs"
              @click.stop="minimize"
              style="z-index: 2"
            >
              <q-tooltip>Minimize</q-tooltip>
            </q-btn>
          </div>
        </template>
        <q-separator inset :color="color" style="opacity: 0.3" />
        <div class="relative-position">
          <slot />
        </div>
      </q-expansion-item>
    </template>
    <template v-else>
      <div
        class="full-width row q-pr-lg items-center text-h5 q-py-sm relative-position header-tint"
        :class="[`text-${color}`, titleEnd ? 'justify-end' : 'justify-center']"
      >
        <q-icon :name="icon" class="q-mr-sm" size="sm" style="opacity: 0.7" />
        <slot name="title">
          <span class="text-weight-bold">{{ title }}</span>
        </slot>
        <slot name="header-extra" />
        <q-btn
          v-if="minimizable && !isMobile"
          flat
          round
          dense
          icon="close"
          size="sm"
          class="minimize-btn absolute-top-right q-ma-xs"
          @click="minimize"
          style="z-index: 2"
        >
          <q-tooltip>Minimize</q-tooltip>
        </q-btn>
      </div>
      <q-separator inset :color="color" style="opacity: 0.3" />
      <div class="relative-position">
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
  overflow: hidden;
  transition: all 0.3s ease;
}

.section-gradient {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  position: relative;
}

.shadow-subtle {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.border-subtle {
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.with-opacity {
  background: rgba(0, 0, 0, 0.01);
}

.header-tint {
  background: rgba(0, 0, 0, 0.015);
}

.section-watermark {
  z-index: 0;
}
</style>

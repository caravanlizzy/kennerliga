<template>
  <div
    v-if="!isMinimized"
    :class="[
      bordered ? `border-2 rounded-borders border-${color}` : '',
      { 'bg-grey-2': !bordered, 'bg-white': bordered }
    ]"
    class="q-mt-md content-section-container rounded-borders"
  >
    <template v-if="expandable">
      <q-expansion-item
        v-model="isOpened"
        dense-toggle
        expand-separator
        expand-icon="expand_more"
        expanded-icon="expand_less"
        :expand-icon-class="`text-${color}`"
        :expanded-icon-class="`text-${color}`"
        :header-class="`text-${color} text-h5 q-py-xs justify-center with-opacity relative-position`"
      >
        <template #header>
          <div class="full-width row justify-center items-center">
            <slot name="title">
              {{ title }}
            </slot>
            <slot name="header-extra" />
            <q-btn
              v-if="minimizable"
              flat
              round
              dense
              icon="close"
              size="sm"
              class="minimize-btn absolute-right q-ma-xs"
              @click.stop="minimize"
            >
              <q-tooltip>Minimize</q-tooltip>
            </q-btn>
          </div>
        </template>
        <q-separator inset :color="color" />
        <div>
          <slot />
        </div>
      </q-expansion-item>
    </template>
    <template v-else>
      <div
        class="full-width row q-pr-lg items-center text-h5 q-py-xs relative-position"
        :class="[`text-${color}`, titleEnd ? 'justify-end' : 'justify-center']"
      >
        <slot name="title">
          {{ title }}
        </slot>
        <slot name="header-extra" />
        <q-btn
          v-if="minimizable"
          flat
          round
          dense
          icon="close"
          size="sm"
          class="minimize-btn absolute-right q-ma-xs"
          @click="minimize"
        >
          <q-tooltip>Minimize</q-tooltip>
        </q-btn>
      </div>
      <q-separator inset :color="color" />
      <slot />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useUiStore } from 'src/stores/uiStore';

const uiStore = useUiStore();

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

<style scoped>
.content-section-container {
  overflow: hidden;
}

.with-opacity {
  background: rgba(0, 0, 0, 0.01);
}
</style>

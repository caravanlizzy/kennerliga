<!-- CollapsibleSidePanel.vue -->
<template>
  <div class="row no-wrap items-stretch">
    <!-- Main content -->
    <div class="col min-w-0" :class="[{ 'q-pr-md': !isSmall }]">
      <slot />
    </div>

    <!-- Large screens: separator + fixed panel -->
    <template v-if="!isSmall">
      <div
        class="col-auto"
        :style="{ width: props.sideWidth + 'px', flex: '0 0 auto' }"
      >
        <slot name="side" />
      </div>
    </template>

    <!-- Small screens: Drawer + full-height slim rail when closed -->
    <template v-else>
      <KennerButton
        v-if="!sideOpen"
        dense
        flat
        no-caps
        ripple
        :style="{
          position: 'fixed',
          top: '50%',
          right: 0,
          transform: 'translateY(-50%)',
          width: props.railWidth + 'px',
          minWidth: props.railWidth + 'px',
          height: '120px',
          borderRadius: '8px 0 0 8px',
          zIndex: 2002,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: 'var(--q-dark)', // or use a class
          color: 'white',
          fontWeight: '600',
          writingMode: 'vertical-rl',
        }"
        @click="toggleSide"
      >
        {{ props.sideTitle }}
      </KennerButton>

      <q-drawer
        v-model="sideOpen"
        side="right"
        behavior="mobile"
        overlay
        :width="sideWidth"
        :elevated="true"
      >
        <q-toolbar class="q-px-md">
          <q-toolbar-title class="ellipsis">{{
            props.sideTitle
          }}</q-toolbar-title>
          <KennerButton
            flat
            round
            dense
            icon="close"
            @click="toggleSide"
          />
        </q-toolbar>
        <q-separator />
        <div class="q-pa-md">
          <slot name="side" />
        </div>
      </q-drawer>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useResponsive } from 'src/composables/responsive';
import KennerButton from 'components/base/KennerButton.vue';

type Break = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

type Props = {
  /** Sidebar title used on the rail and drawer header */
  sideTitle?: string;
  /** Sidebar width on large screens (px) */
  sideWidth?: number;
  /** Rail thickness on small screens (px) */
  railWidth?: number;
  /** Treat screens <= this breakpoint as "small" (defaults to 'md') */
  switchAt?: Break;
  /** Start collapsed on small screens */
  collapsedSmallByDefault?: boolean;
};

const props = withDefaults(defineProps<Props>(), {
  sideTitle: 'Details',
  sideWidth: 350,
  railWidth: 28,
  switchAt: 'sm',
  collapsedSmallByDefault: true,
});

/** Use your composable; grab screenName specifically */
const { screenName } = useResponsive();

/** Determine if we're on a "small" screen using screenName */
const order: Break[] = ['xs', 'sm', 'md', 'lg', 'xl'];
const isSmall = computed(() => {
  const cur = order.indexOf(screenName.value);
  const cut = order.indexOf(props.switchAt);
  return cur <= cut;
});

/** Open state: large screens always open; small screens follow default & toggles */
const sideOpen = ref(true);
watch(
  isSmall,
  (small) => {
    sideOpen.value = small ? !props.collapsedSmallByDefault : true;
  },
  { immediate: true }
);

function toggleSide() {
  sideOpen.value = !sideOpen.value;
}
</script>

<style scoped>
.min-w-0 {
  min-width: 0;
}
/* ultra-minimal helper for vertical rail text */
.vertical-label {
  writing-mode: vertical-rl;
  text-orientation: mixed;
  font-weight: 600;
}
</style>

<!-- CollapsibleSidePanel.vue -->
<template>
  <div class="row no-wrap items-stretch full-height relative-position">
    <!-- Main content -->
    <div class="col min-w-0" :class="[{ 'q-pr-md': !isSmall }]">
      <slot />
    </div>

    <!-- Large screens: panel -->
    <template v-if="!isSmall">
      <div
        class="col-auto glass-sidebar"
        :style="{ width: props.sideWidth + 'px', flex: '0 0 auto' }"
      >
        <div class="q-pa-md">
          <div class="row items-center q-mb-md">
            <div class="bg-primary header-indicator q-mr-sm" />
            <div class="text-h6 text-weight-bold text-primary tracking-tight">{{ props.sideTitle }}</div>
          </div>
          <slot name="side" />
        </div>
      </div>
    </template>

    <!-- Small screens: Drawer + floating toggle -->
    <template v-else>
      <div
        v-if="!sideOpen"
        class="fixed-bottom-right q-ma-md"
        style="z-index: 2000"
      >
        <q-btn
          round
          size="lg"
          color="primary"
          icon="leaderboard"
          class="shadow-10"
          @click="toggleSide"
        >
          <q-badge floating color="accent" rounded />
        </q-btn>
      </div>

      <q-drawer
        v-model="sideOpen"
        side="right"
        behavior="mobile"
        overlay
        :width="sideWidth"
        class="glass-sidebar-drawer"
      >
        <div class="column full-height">
          <q-toolbar class="q-px-md glass-header text-primary">
            <div class="bg-primary header-indicator q-mr-sm" />
            <q-toolbar-title class="text-weight-bold tracking-tight">
              {{ props.sideTitle }}
            </q-toolbar-title>
            <q-btn
              flat
              round
              dense
              color="primary"
              icon="close"
              @click="toggleSide"
            />
          </q-toolbar>
          <q-separator class="opacity-10" />
          <div class="col scroll q-pa-md">
            <slot name="side" />
          </div>
        </div>
      </q-drawer>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useResponsive } from 'src/composables/responsive';

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

/** Open state: small screens follow default & toggles */
const sideOpen = ref(false);
watch(
  isSmall,
  (small) => {
    if (!small) {
      sideOpen.value = false; // reset for mobile when returning to desktop
    } else {
      sideOpen.value = !props.collapsedSmallByDefault;
    }
  },
  { immediate: true }
);

function toggleSide() {
  sideOpen.value = !sideOpen.value;
}
</script>

<style scoped lang="scss">
.min-w-0 {
  min-width: 0;
}

.glass-sidebar {
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(12px);
  border-left: 1px solid rgba(54, 64, 88, 0.08);
  height: calc(100vh - 120px); // Adjust based on navbar/footer height if needed
  position: sticky;
  top: 80px;
  overflow-y: auto;
}

.glass-sidebar-drawer {
  background: rgba(255, 255, 255, 0.9) !important;
  backdrop-filter: blur(16px);
}

.glass-header {
  background: transparent;
  min-height: 64px;
}

.header-indicator {
  width: 4px;
  height: 24px;
  border-radius: 4px;
}

.tracking-tight {
  letter-spacing: -0.02em;
}

.opacity-10 {
  opacity: 0.1;
}
</style>

<!-- CollapsibleSidePanel.vue -->
<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useResponsive } from 'src/composables/reponsive';

type Break = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

type Props = {
  /** Sidebar title used on the rail and drawer header */
  sideTitle?: string
  /** Sidebar width on large screens (px) */
  sideWidth?: number
  /** Rail thickness on small screens (px) */
  railWidth?: number
  /** Treat screens <= this breakpoint as "small" (defaults to 'md') */
  switchAt?: Break
  /** Start collapsed on small screens */
  collapsedSmallByDefault?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  sideTitle: 'Details',
  sideWidth: 300,
  railWidth: 28,
  switchAt: 'sm',
  collapsedSmallByDefault: true
})

/** Use your composable; grab screenName specifically */
const { screenName } = useResponsive()

/** Determine if we're on a "small" screen using screenName */
const order: Break[] = ['xs', 'sm', 'md', 'lg', 'xl']
const isSmall = computed(() => {
  const cur = order.indexOf(screenName.value)
  const cut = order.indexOf(props.switchAt)
  return cur <= cut
})

/** Open state: large screens always open; small screens follow default & toggles */
const sideOpen = ref(true)
watch(isSmall, (small) => {
  sideOpen.value = small ? !props.collapsedSmallByDefault : true
}, { immediate: true })

function toggleSide () {
  sideOpen.value = !sideOpen.value
}
</script>

<template>
  <div class="row no-wrap items-stretch">
    <!-- Main content -->
    <div class="col min-w-0">
      <slot />
    </div>

    <!-- Large screens: separator + fixed panel -->
    <template v-if="!isSmall">
      <q-separator vertical />
      <div class="col-auto" :style="{ width: props.sideWidth + 'px', flex: '0 0 auto' }">
        <slot name="side" />
      </div>
    </template>

    <!-- Small screens: Drawer + full-height slim rail when closed -->
    <template v-else>
      <q-btn
        v-if="!sideOpen"
        dense
        flat
        no-caps
        ripple
        :style="{
          position: 'fixed',
          top: 0,
          right: 0,
          height: '100dvh',
          width: props.railWidth + 'px',
          minWidth: props.railWidth + 'px',
          borderRadius: 0,
          padding: 0,
          zIndex: 2000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }"
        class="vertical-label q-pa-none"
        :aria-label="`Open ${props.sideTitle}`"
        @click="toggleSide"
      >
        {{ props.sideTitle }}
      </q-btn>

      <q-drawer
        v-model="sideOpen"
        side="right"
        behavior="mobile"
        overlay
        :width="Math.min(props.sideWidth, 480)"
        :elevated="true"
      >
        <q-toolbar class="q-px-md">
          <q-toolbar-title class="ellipsis">{{ props.sideTitle }}</q-toolbar-title>
          <q-btn flat round dense icon="close" :aria-label="`Close ${props.sideTitle}`" @click="toggleSide" />
        </q-toolbar>
        <q-separator />
        <div class="q-pa-md">
          <slot name="side" />
        </div>
      </q-drawer>
    </template>
  </div>
</template>

<style scoped>
.min-w-0 { min-width: 0; }
/* ultra-minimal helper for vertical rail text */
.vertical-label { writing-mode: vertical-rl; text-orientation: mixed; font-weight: 600; }
</style>

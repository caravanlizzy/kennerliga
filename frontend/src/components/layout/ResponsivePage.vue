<template>
  <component :is="isMobile ? mobileComp : desktopComp" />
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent, type Component, type AsyncComponentLoader } from 'vue';
import { useResponsive } from 'src/composables/responsive';

const props = defineProps<{
  desktop: Component | AsyncComponentLoader;
  mobile: Component | AsyncComponentLoader;
}>();

const { isMobile } = useResponsive();

function resolve(c: Component | AsyncComponentLoader): Component {
  // If it's a plain function (async loader returning a Promise), wrap it.
  if (typeof c === 'function') {
    return defineAsyncComponent(c as AsyncComponentLoader);
  }
  return c;
}

const desktopComp = computed(() => resolve(props.desktop));
const mobileComp = computed(() => resolve(props.mobile));
</script>

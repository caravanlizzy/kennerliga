<template>
  <KennerButton
    flat
    dense
    shape="squircle"
    :icon="themeIcon"
    color="grey-7"
    class="nav-section-btn"
    style="height: 40px; min-width: 40px;"
    @click="themeStore.toggleDark()"
  >
    <KennerTooltip>{{ tooltipText }}</KennerTooltip>
  </KennerButton>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useThemeStore } from 'stores/themeStore';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';

const themeStore = useThemeStore();

const themeIcon = computed(() => {
  return themeStore.isDark ? 'light_mode' : 'dark_mode';
});

const tooltipText = computed(() => {
  return themeStore.isDark ? 'Switch to light mode' : 'Switch to dark mode';
});
</script>

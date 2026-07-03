<template>
  <div class="row items-center no-wrap">
    <KennerButton
      :to="{ name: isMobile ? 'season-standings' : 'home' }"
      unelevated
      flat
      color="dark"
      :class="[isMobile ? 'q-px-xs' : 'q-px-md', 'text-weight-bold']"
      style="height: 44px; min-width: 44px;"
    >
      <BrandLogo :compact="isMobile" />
    </KennerButton>
  </div>
</template>

<script setup lang="ts">
import { useResponsive } from 'src/composables/responsive';
import KennerButton from 'components/base/KennerButton.vue';
import BrandLogo from 'components/base/BrandLogo.vue';

const { isMobile } = useResponsive();
</script>

<style scoped lang="scss">
:deep(.q-btn__content) {
  text-transform: none;
}
</style>

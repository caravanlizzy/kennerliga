<template>
  <div class="row items-center no-wrap">
    <KennerButton
      :to="{ name: 'home' }"
      unelevated
      flat
      color="dark"
      :class="[isMobile ? 'q-px-xs' : 'nav-item-radius', 'text-weight-bold']"
      style="height: 40px; min-width: 40px; border-radius: 0 !important;"
    >
      <div class="row items-center no-wrap">
        <q-icon size="md" name="img:icons/favicon.svg" class="q-mr-sm" />
        <span v-if="!isMobile" class="text-h5 text-dark text-weight-bold tracking-tight" style="letter-spacing: -0.5px;">Kenner<span class="text-accent">Liga</span></span>
      </div>
    </KennerButton>

  </div>
</template>
<script setup lang="ts">
import { useResponsive } from 'src/composables/responsive';
import KennerButton from 'components/base/KennerButton.vue';

const { isMobile } = useResponsive();

</script>

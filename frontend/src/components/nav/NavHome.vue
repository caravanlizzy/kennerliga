<template>
  <div class="row items-center no-wrap">
    <KennerButton
      :to="{ name: 'home' }"
      unelevated
      flat
      color="dark"
      class="nav-item-radius text-weight-bold"
    >
      <div class="row items-center no-wrap">
        <q-icon size="md" name="img:icons/favicon.svg" class="q-mr-sm" />
        <span v-if="!isMobile" class="text-h5 text-dark text-weight-bold tracking-tight" style="letter-spacing: -0.5px;">KennerLiga</span>
      </div>
    </KennerButton>

  </div>
</template>
<script setup lang="ts">
import { useResponsive } from 'src/composables/responsive';
import KennerButton from 'components/base/KennerButton.vue';

const { isMobile } = useResponsive();

</script>

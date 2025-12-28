<template>
  <div class="row items-center no-wrap">
    <KennerButton
      :to="{ name: 'home' }"
      unelevated
      flat
      color="primary"
      class="nav-item-radius text-weight-bold"
    >
      <q-icon size="sm" name="img:icons/favicon.svg" />
    </KennerButton>

  </div>
</template>
<script setup lang="ts">
import { useResponsive } from 'src/composables/responsive';
import KennerButton from 'components/base/KennerButton.vue';

const { isMobile } = useResponsive();

</script>

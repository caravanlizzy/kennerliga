<template>
  <div class="row items-center no-wrap">
    <q-btn
      :to="{ name: 'home' }"
      unelevated
      flat
      color="primary"
      class="nav-item-radius text-weight-bold"
    >
      <q-icon size="sm" name="img:icons/favicon.svg" />
    </q-btn>

  </div>
</template>
<script setup lang="ts">
import { useResponsive } from 'src/composables/responsive';

const { isMobile } = useResponsive();

</script>

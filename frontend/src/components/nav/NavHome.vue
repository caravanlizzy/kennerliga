<template>
  <div class="row items-center no-wrap">
    <q-btn
      :to="{ name: 'home' }"
      unelevated
      bordered
      color="white"
      class="primary-border nav-item-radius text-weight-medium"
    >
      <q-icon size="sm" name="img:icons/favicon.svg" />
    </q-btn>

  </div>
</template>
<script setup lang="ts">
import { useResponsive } from 'src/composables/responsive';

const { isMobile } = useResponsive();

</script>

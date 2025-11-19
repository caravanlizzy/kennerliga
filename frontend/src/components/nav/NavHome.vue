<template>
  <div class="row items-center no-wrap">
    <q-btn
      v-if="isMobile"
      :to="{ name: 'home' }"
      unelevated
      bordered
      color="white"
      class="info-border nav-item-radius text-weight-medium"
    >
      <q-icon  color="info" name="psychology" />
    </q-btn>
    <q-btn
      v-else
      :to="{ name: 'home' }"
      unelevated
      color="white"
      text-color="info"
      class="info-border nav-item-radius text-weight-medium"
      no-caps
    >
      <q-icon color="info" name="psychology" />
      <span v-show="!isMobile" class="q-ml-xs">Kennerliga</span>
    </q-btn>

  </div>
</template>
<script setup lang="ts">
import { useResponsive } from 'src/composables/reponsive';

const { isMobile } = useResponsive();

</script>

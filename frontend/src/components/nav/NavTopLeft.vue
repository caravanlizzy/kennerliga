<template>
  <q-toolbar-title shrink class="text-secondary">
      <q-btn :to="{ name: 'home' }" flat :size="iconSize" outlined icon="pets" />
  </q-toolbar-title>
</template>

<script setup lang="ts">
import { useResponsive } from 'src/composables/reponsive';

const { iconSize } = useResponsive();
</script>

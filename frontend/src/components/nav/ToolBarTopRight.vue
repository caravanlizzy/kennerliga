<template>
  <div class="row no-wrap">
    <q-btn stretch :size="iconSize" flat icon="settings"></q-btn>
    <q-btn stretch :size="iconSize" flat icon="logout" color="negative" />
  </div>
</template>
<script setup lang="ts">

import { useResponsive } from 'src/composables/reponsive';

const { iconSize } = useResponsive();

</script>

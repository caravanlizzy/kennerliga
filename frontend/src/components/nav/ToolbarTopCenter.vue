<template>
  <div class="row no-wrap">
    <q-btn :size="iconSize" stretch flat color="secondary" :dense="isMobile" icon="add_circle">
      <q-tooltip class="bg-secondary text-primary" delay="50" hide-delay="50" > Ergebnis eintragen</q-tooltip>
    </q-btn>
    <q-btn :size="iconSize" :to="{ name:'games' }" :dense="isMobile" stretch flat icon="casino"></q-btn>
    <q-btn :size="iconSize" :to="{ name: 'users' }" stretch :dense="isMobile" flat icon="person"></q-btn>
  </div>
</template>
<script setup lang="ts">
import { useResponsive } from 'src/composables/reponsive';

const { iconSize, isMobile } = useResponsive()

</script>


<style scoped>
.q-btn {
  margin: 0 10px;
}
</style>

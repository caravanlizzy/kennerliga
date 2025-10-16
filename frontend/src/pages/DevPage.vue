<template>
  <div class="q-pa-md">
    <DevTools />
    <q-btn label="Create Season and Leagues" :to="{ name: 'season-create' }" />
  </div>
</template>

<script setup lang="ts">
import DevTools from 'components/ui/DevTools.vue';
</script>

<style scoped></style>

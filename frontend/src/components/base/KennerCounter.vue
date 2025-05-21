<template>
  <div class="q-pa-sm text-accent text-h6 row flex-center">{{content + 1}}</div>
</template>

<script setup lang="ts">
defineProps<{ content: number }>();
</script>

<style scoped>

</style>

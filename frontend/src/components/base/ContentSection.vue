<template>
  <div class="section"
       :style="`border-color: var(--q-${color})`"
  >
    <div
      class="text-h5 q-py-xs row justify-center"
      :class="`bg-${color} text-white`"
    >
      {{ title }}
    </div>
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; color: string }>();
</script>

<style scoped>
.section {
  border: 3px solid;
}
</style>

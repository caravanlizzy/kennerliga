<template>
  <AvatarShapeSvgDefs />
  <Suspense>
    <router-view />
  </Suspense>
</template>

<script setup lang="ts">
import AvatarShapeSvgDefs from 'components/ui/AvatarShapeSvgDefs.vue';
</script>

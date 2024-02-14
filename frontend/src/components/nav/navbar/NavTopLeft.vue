<template>
  <div class="">
      <kenner-button :to="{ name: 'home' }" flat color="accent" :size="iconSize" icon="pets" />
  </div>
</template>

<script setup lang="ts">
import { useResponsive } from 'src/composables/reponsive';
import KennerButton from 'components/buttons/KennerButton.vue';

const { iconSize } = useResponsive();
</script>

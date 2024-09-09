<template>
  <PlayerOrderList/>
  <GameSelector v-if="isActive" />
</template>

<script setup lang="ts">

import GameSelector from 'components/singles/GameSelector.vue';
import { ref } from 'vue';
import PlayerOrderList from 'components/lists/PlayerOrderList.vue';

const isActive = ref(true);
</script>

<style scoped>

</style>

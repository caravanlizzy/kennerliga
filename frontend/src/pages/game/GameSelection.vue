<template>
  <div class="q-pa-lg">
    <StatusBar> Pending...</StatusBar>
    <PlayerOrderList/>
    <GameSelector v-if="isActive"/>
  </div>
</template>

<script setup lang="ts">

import GameSelector from 'components/singles/GameSelector.vue';
import { ref } from 'vue';
import PlayerOrderList from 'components/lists/PlayerOrderList.vue';
import StatusBar from "components/StatusBar.vue";

const isActive = ref(true);
</script>

<style scoped>

</style>

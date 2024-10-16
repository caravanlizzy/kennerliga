<template>
  <div class="q-pa-lg">
    <div class="gradient">
      <StatusBar> Pending...</StatusBar>
      <PlayerOrderList class="bg-grey-2"/>
    </div>
    <GameSelector v-if="isActive" class="q-mt-md"/>
  </div>
</template>

<script setup lang="ts">

import GameSelector from 'components/singles/GameSelector.vue';
import { ref } from 'vue';
import PlayerOrderList from 'components/lists/PlayerOrderList.vue';
import StatusBar from "components/StatusBar.vue";

const isActive = ref(true);
</script>


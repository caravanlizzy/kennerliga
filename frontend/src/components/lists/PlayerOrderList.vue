<template>
  <div class="row">
    <div v-for="player of players" :key="player.name" class="q-mx-lg row">
      <div :class="{ 'active-player' : activePlayer === player.name }">
        <div>{{ player.name }}</div>
        <div>{{ player.game }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">

import { ref } from 'vue';

const players = [
  { name: 'haligh', game: 'Terra Mystica' },
  { name: 'isiundossi', game: 'Gaia Project' },
  { name: 'Ginooo', game: '7 Wonders' },
  { name: 'MissM', game: 'Automobiles' }
];

const activePlayer = ref('haligh');

</script>

<style scoped lang="scss">
.active-player {
  border-bottom: 3px solid $accent;
  padding: 6px;
}
</style>

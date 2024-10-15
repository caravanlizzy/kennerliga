<template>
  <div class="row">
    <div v-for="player of players" :key="player.name" class="q-mr-lg row">
      <div :class="{ 'active-player' : activePlayer === player.name }">
        <div :class="{isMeClass: isMe(player.name)}">{{ player.name }}</div>
        <div>{{ player.game }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">

import { ref } from 'vue';
import { useUserStore } from 'stores/userStore';

const { isMe } = useUserStore();

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

.isMeClass {
  text-decoration: underline;
}
</style>

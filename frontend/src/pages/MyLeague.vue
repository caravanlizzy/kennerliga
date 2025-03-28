<template>
  <div class="q-pa-lg">
    <div class="gradient">
      <StatusBar> Pending...</StatusBar>
      <KennerButton @click="next"> Next</KennerButton>
      <PlayerOrderList class="bg-grey-2" />
    </div>
    <GameSelector v-if="isActive" class="q-mt-lg" />
  </div>
</template>

<script setup lang="ts">
import GameSelector from 'components/ui/GameSelector.vue';
import { ref } from 'vue';
import PlayerOrderList from 'components/lists/PlayerOrderList.vue';
import StatusBar from 'components/StatusBar.vue';
import KennerButton from 'components/buttons/KennerButton.vue';
import { api } from 'boot/axios';

const league = ref(null);

api({
  url: '/league/leagues/',
  method: 'GET',
}).then(({ data }) => {
  league.value = data;
});

function next() {
  api({
    url: '/league/1/next-player/',
    method: 'POST',
  }).then(({ data }) => {
    console.log(data);
  });
}

const isActive = ref(true);
</script>

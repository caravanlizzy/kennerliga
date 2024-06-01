<template>
  <div class="q-pa-lg">
    <div class="text-h6"> Wähle dein Spiel</div>
    <div class="row q-gutter-md">
      <kenner-select style="width: 130px"
                     v-model="platform" option-value="name" option-label="name" :options="platforms"
                     label="Platform" />
      <q-input v-model="filter" label="Filter">
        <template v-slot:append>
          <q-icon v-if="filter !== ''" name="close" @click="filter = ''" class="cursor-pointer" />
          <q-icon name="search" />
        </template>
      </q-input>
    </div>
    <div class="row">
      <q-btn @click="selectedGame = game" flat class="q-pa-xs q-ma-md text-primary" v-for="game of games" :key="game.id">
        <div class=" q-pa-xs bg-white">
          {{ game.name }}
        </div>
      </q-btn>
    </div>
    <div class="q-py-md">
      <span class="text-h6">Wähle Optionen - {{ selectedGame.name }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import KennerSelect from 'components/inputs/KennerSelect.vue';
import { api } from 'boot/axios';
import { computed, Ref, ref } from 'vue';
import { GameDto, TPlatform } from 'pages/game/models';
import { symRoundedFoggy } from '@quasar/extras/material-symbols-rounded';

const { data: platforms } = await api('game/platforms/');
const { data: gameData } = await api('game/games/');

function filterGames() {
  let games = gameData;
  if (!platform.value) return [];
  else {
    games = games.filter(game => game.platform === platform.value.id);
  }
  if (filter.value !== '') {
    games = games.filter((game) => game.name.toLowerCase().includes(filter.value.toLowerCase()));
  }
  return games;

}

const games = computed(() => filterGames());
const platform: Ref<TPlatform | undefined> = ref(undefined);
const filter = ref('');
const selectedGame:Ref<GameDto|undefined> = ref(undefined);
</script>

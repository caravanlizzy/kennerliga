<template>
  <div class="q-pa-lg">
    <div class="text-h6"> Wähle dein Spiel</div>
    <div class="row q-gutter-md">
      <kenner-select style="width: 130px"
                     v-model="platform" option-value="name" option-label="name" :options="platforms"
                     label="Platform" />
      <q-input v-model="filter" label="Suche">
        <template v-slot:append>
          <q-icon v-if="filter !== ''" name="close" @click="filter = ''" class="cursor-pointer" />
          <q-icon name="search" />
        </template>
      </q-input>
    </div>
    <div class="row q-my-lg">
      <div @click="selectedGame = game" v-for="game of games" :key="game.id">
        <div class="q-px-lg q-py-md text-bold game-selection-element"
             :class="{'selected': selectedGame && game.id === selectedGame.id}">
          {{ game.name.toUpperCase() }}
        </div>
      </div>
    </div>
    <div v-if="selectedGame" class="q-py-md">
      <span class="text-h6"> {{ selectedGame.name.toUpperCase() }} </span>
      <div v-if="selectedGameOptions && selectedGameOptions.length === 0 " class="text-italic"> Spiel hat keine weiteren
        Optionen
      </div>
      <template v-else>
        <div class="text-h6"> Spieloptionen</div>
        <div v-for="option of selectedGameOptions" :key="option.id">
          {{ option.name }}
          <template v-if="option.has_choices">
            <kenner-select :options="getOptionChoices(option)" label="Option" option-label="name" option-value="name" :model-value="test" ></kenner-select>
          </template>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import KennerSelect from 'components/inputs/KennerSelect.vue';
import { api } from 'boot/axios';
import { computed, Ref, ref, watch } from 'vue';
import { GameDto, GameOptionChoiceDtp, GameOptionDto, TGameOption, TPlatform } from 'pages/game/models';

const { data: platforms } = await api('game/platforms/');
const { data: gameData } = await api('game/games/');


const platform: Ref<TPlatform | undefined> = ref(undefined);
const filter = ref('');
const selectedGame: Ref<GameDto | undefined> = ref(undefined);
const selectedGameOptions: Ref<GameOptionDto[] | undefined> = ref(undefined);
const test = ref('');

const games = computed(() => filterGames());
watch(selectedGame, getGameOptions);

async function getGameOptions(): Promise<void> {
  if (!selectedGame.value) return;
  const { data } = await api(`game/options/?game=${selectedGame.value.id}`);
  selectedGameOptions.value = data;
}

async function getOptionChoices(option: GameOptionDto): Promise<GameOptionChoiceDtp> {
  const { data } =  await api(`game/option-choices/?option=${option.id}`);
  return data;
}

function filterGames() {
  let games = gameData;
  if (platform.value === undefined) return [];
  else {
    games = games.filter(game => game.platform === platform.value.id);
  }
  if (filter.value !== '') {
    games = games.filter((game) => game.name.toLowerCase().includes(filter.value.toLowerCase()));
  }
  return games;
}

</script>


<style lang="scss">
@import 'src/css/quasar.variables.scss';

.game-selection-element {
  outline: 6px solid white;
  background-color: $secondary;
  transition: background-color 0.5s ease;
  color: white;

  &:hover {
    color: $primary;
  }
}

.selected {
  background-color: $primary;

  &:hover {
    color: $accent;
  }
}
</style>

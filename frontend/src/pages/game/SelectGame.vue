<template>
  <div class="q-pa-lg">
    <div class="text-h6"> Wähle dein Spiel</div>
    <div class="row q-gutter-md">
      <kenner-select class="select-width q-mr-md"
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
        <div class="q-px-lg q-py-md text-bold game-selection-element cursor-pointer"
             :class="{'selected': selectedGame && game.id === selectedGame.id}">
          {{ game.name.toUpperCase() }}
        </div>
      </div>
    </div>
    <div v-if="selectedGame" class="q-py-md">
      <span class="text-h6"> {{ selectedGame.name.toUpperCase() }} </span>
      <div v-if="fullGameInformation.options && fullGameInformation.options.length === 0 " class="text-italic"> Spiel
        hat keine weiteren
        Optionen
      </div>
      <template v-else>
        <div class="text-h6 q-py-md"> Spieloptionen einstellen</div>
        <div v-for="option of fullGameInformation.options" :key="option.id" class="q-py-sm">
            <template v-if="option.has_choices">
              <kenner-select
                :options="fullGameInformation.options.find(o => o.id === option.id).choices"
                :label="option.name"
                option-label="name"
                v-model="selectedOptions[option.id]"
                class="select-width inline-block"
              />
            </template>
            <template v-else>
              <q-toggle
                :model-value="selectedOptions[option.id]"
                @update:model-value="selectedOptions[option.id] = !selectedOptions[option.id]"
                :label="option.name"
              />
            </template>
        </div>
      </template>
    </div>
    <kenner-button class="" type="submit" push color="positive" label="Speichern" />
  </div>
</template>

<script setup lang="ts">
import KennerSelect from 'components/inputs/KennerSelect.vue';
import { api } from 'boot/axios';
import { computed, Ref, ref, watch } from 'vue';
import { GameDto, TPlatform } from 'pages/game/models';
import KennerButton from 'components/buttons/KennerButton.vue';
import { useUserStore } from 'stores/userStore';


const { user } = useUserStore();
const { data: platforms } = await api('game/platforms/');
const { data: gameData } = await api('game/games/');


const platform: Ref<TPlatform | undefined> = ref(undefined);
const filter = ref('');
const selectedGame: Ref<GameDto | undefined> = ref(undefined);
const selectedOptions = ref({}); //key value store
const fullGameInformation = ref({});

const games = computed(() => filterGames());
watch(selectedGame, updateGameInformation);

async function updateGameInformation(): Promise<void> {
  if (!selectedGame.value) return;
  const { data: options } = await api(`game/options/?game=${selectedGame.value.id}`);
  fullGameInformation.value['options'] = options;
  for (const option of options) {
    if (option.has_choices) {
      selectedOptions.value[option.id] = null;
      const { data: choices } = await api(`game/option-choices/?option=${option.id}`);
      fullGameInformation.value.options.find(o => o.id === option.id)['choices'] = choices;
    } else {
      selectedOptions.value[option.id] = false;

    }
  }
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

.select-width {
  width: 140px;
}

</style>

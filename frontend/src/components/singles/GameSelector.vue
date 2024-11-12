<template>
  <div class="">
    <div class="text-h6">Wähle dein Spiel</div>
    {{ gameSelection }}
    <div class="row">
      <kenner-select
        class="select-width q-mr-md"
        v-model="platform"
        option-value="name"
        option-label="name"
        :options="platforms"
        label="Platform"
      />
      <q-input v-model="filter" label="Spiel">
        <template v-slot:append>
          <q-icon
            v-if="filter !== ''"
            name="close"
            @click="filter = ''"
            class="cursor-pointer"
          />
          <q-icon name="search" />
        </template>
      </q-input>
    </div>
    <div class="row games-container q-mt-lg">
      <div
        @click="setGameInformation(game)"
        v-for="game of games"
        :key="game.id"
      >
        <div
          class="q-px-lg q-py-md game-selection-element cursor-pointer"
          :class="{
            selected:
              gameInformation.game && game.id === gameInformation.game.id,
          }"
        >
          {{ game.name.toUpperCase() }}
        </div>
      </div>
    </div>
    <div v-if="gameInformation.game" class="q-py-md q-my-md">
      <span class="text-h6"> {{ gameInformation.game.name }} </span>
      <div
        v-if="gameInformation.options && gameInformation.options.length === 0"
        class="text-italic"
      >
        Spiel hat keine weiteren Optionen
      </div>
      <template v-else>
        <div
          v-for="option of gameInformation.options"
          :key="option.id"
          class="q-py-sm"
        >
          <template v-if="option.has_choices">
            <kenner-select
              :options="findChoicesByOption(option.id)"
              :label="option.name"
              option-label="name"
              v-model="gameSelection.selected_options.find((o) => o.id == option.id).choice"
              class="select-width inline-block"
            />
          </template>
          <template v-else>
            <q-toggle
              v-model="
                gameSelection.selected_options.find((o) => o.id == option.id)
                  .value
              "
              :label="option.name"
            />
          </template>
        </div>
      </template>
    </div>
    <KennerButton
      @click="submitGame"
      type="submit"
      push
      color="positive"
      label="Speichern"
    />
  </div>
</template>

<script setup lang="ts">
import KennerSelect from 'components/inputs/KennerSelect.vue';
import { api } from 'boot/axios';

import KennerButton from 'components/buttons/KennerButton.vue';
import { computed, reactive, ref, Ref } from 'vue';
import {
  GameDto,
  GameOptionDto,
  SelectedGameDto,
  SelectedGameOptionDto,
  TPlatform,
} from 'src/models/gameModels';
import {
  createSelectedGame,
  getGameOptionChoices,
  getGameOptions,
} from 'src/services/game/selectGameService';

const gameInformation = reactive<{
  game: GameDto | undefined;
  options: GameOptionDto[];
}>({
  game: undefined,
  options: [],
});

const gameSelection = reactive<SelectedGameDto>({
  game: 0, // Assign a default game ID or handle appropriately
  selected_options: [],
});

function loadGame(game: GameDto) {
  gameInformation.game = game;
  gameSelection.game = game.id;
  gameInformation.options = [];
  gameSelection.selected_options = [];
}

async function setGameInformation(game: GameDto) {
  if(gameInformation.game && gameInformation.game.id === game.id) return;
  loadGame(game);
  await loadOptions(game.id);
  await loadChoices();
}

function setSelectedOption(option: GameOptionDto) {
  const selectedOption: SelectedGameOptionDto = {
    id: option.id,
    selected_game: gameSelection.game,
    value: undefined,
    choice: undefined,
  };
  if (!option.has_choices) {
    selectedOption.value = false;
  }
  gameSelection.selected_options.push(selectedOption);
}

async function loadOptions(gameId: number) {
  try {
    const { data: options } = await getGameOptions(gameId);
    gameInformation.options = options;
    for (const option of options) {
      setSelectedOption(option);
    }
  } catch (error) {
    console.error(`Failed to fetch options for game ${gameId}:`, error);
    gameInformation.options = []; // Clear options on error or handle as needed
  }
}

async function loadChoices() {
  for (let option of gameInformation.options) {
    if (!option.has_choices) continue;
    const optionId = option.id;
    const { data: newChoices } = await getGameOptionChoices(optionId);
    if (!option.choices) option.choices = [];
    option.choices = [...newChoices, ...option.choices];
  }
}

function findChoicesByOption(optionId: number) {
  const option = gameInformation.options.find(
    (option) => option.id === optionId
  );
  if (!option) return null;
  return option.choices;
}

const { data: platforms } = await api('game/platforms/');
const { data: gameData } = await api('game/games/');
//
const platform: Ref<TPlatform | undefined> = ref(undefined);
const games = computed<GameDto[]>(() => filterGames());
const filter = ref('');
function filterGames() {
  let games = gameData || [];
  if (platform.value) {
    games = games.filter((game) => game.platform === platform.value?.id);
  }
  if (filter.value) {
    games = games.filter((game) =>
      game.name.toLowerCase().includes(filter.value.toLowerCase())
    );
  }
  return games;
}

//
function submitGame() {
  if (gameSelection) {
    createSelectedGame(gameSelection);
  } else {
    console.warn('No game selected');
  }
}
</script>

<style lang="scss">
.game-selection-element {
  outline: 0px solid $secondary;
  background-color: white;
  transition: background-color 0.5s ease;
  flex: 1 1 150px;
  color: $primary;

  &:hover {
    color: $info;
  }
}

.selected {
  color: $accent;
  outline: $primary;

  //&:hover {
  //  color: $accent;
  //}
}

.select-width {
  width: 140px;
}

.games-container {
  border-right: 2px solid $secondary;
  border-left: 2px solid $secondary;
}
</style>

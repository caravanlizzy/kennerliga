<template>
  <div>
    <div class="text-h6">Wähle dein Spiel</div>
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
          <q-icon v-if="filter" name="close" @click="filter = ''" class="cursor-pointer" />
          <q-icon name="search" />
        </template>
      </q-input>
    </div>

    <div class="row games-container q-mt-lg">
      <div v-for="game in filteredGames" :key="game.id" @click="setGameInformation(game)">
        <div
          :class="{ selected: gameInformation.game && game.id === gameInformation.game.id }"
          class="q-px-lg q-py-md game-selection-element cursor-pointer"
        >
          {{ game.name.toUpperCase() }}
        </div>
      </div>
    </div>

    <div v-if="gameInformation.game" class="q-py-md q-my-md">
      <span class="text-h6">{{ gameInformation.game.name }}</span>
      <div v-if="!gameInformation.options.length" class="text-italic">Spiel hat keine weiteren Optionen</div>
      <template v-else>
        <div v-for="option in gameInformation.options" :key="option.id" class="q-py-sm">
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
              v-model="gameSelection.selected_options.find((o) => o.id == option.id).value"
              :label="option.name"
            />
          </template>
        </div>
      </template>
    </div>

    <KennerButton @click="submitGame" type="submit" push color="positive" label="Speichern" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import KennerSelect from 'components/inputs/KennerSelect.vue';
import KennerButton from 'components/buttons/KennerButton.vue';
import { useGameSelection } from 'src/composables/gameSelection';

const { gameInformation, gameSelection, setGameInformation, findChoicesByOption, fetchPlatforms, fetchGames, submitGame } = useGameSelection();

const platform = ref();
const filter = ref('');
const platforms = ref([]);
const gameData = ref([]);

onMounted(async () => {
  platforms.value = await fetchPlatforms();
  gameData.value = await fetchGames();
});

const filteredGames = computed(() => {
  return gameData.value.filter((game) => {
    return (!platform.value || game.platform === platform.value.id) && (!filter.value || game.name.toLowerCase().includes(filter.value.toLowerCase()));
  });
});
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

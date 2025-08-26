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
          <q-icon
            v-if="filter"
            name="close"
            @click="filter = ''"
            class="cursor-pointer"
          />
          <q-icon name="search" />
        </template>
      </q-input>
    </div>

    <div class="row games-container q-mt-lg">
      <q-card
        flat
        :bordered="game.id !== gameSelection.game.id"
        v-for="game in filteredGames"
        :key="game.id"
        @click="setGameInformation(game)"
        class="q-ma-sm cursor-pointer hoverable-card"
        :class="{ 'bg-secondary text-white': game.id === gameSelection.game.id }"
        clickable
      >
        <q-card-section>
          <div class="text-subtitle2">{{ game.name }}</div>
          <div class="text-caption">{{ getPlatformName(game.platform) }}</div>
        </q-card-section>
      </q-card>

    </div>

    <div v-if="isLoading">
      <q-spinner-orbit size="xl" />
    </div>
    <div v-else-if="gameInformation.game" class="q-py-md q-my-md">
      <span class="text-h6">{{ gameInformation.game.name }}</span>
      <div v-if="!gameInformation.options.length" class="text-italic">
        Spiel hat keine weiteren Optionen
      </div>
      <template v-else>
        <div
          v-for="option in gameInformation.options"
          :key="option.id"
          class="q-py-sm q-mx-md"
        >
          <div v-if="option.has_choices">
            <kenner-select
              :options="findChoicesByOption(option.id)"
              :label="option.name"
              option-label="name"
              v-model="
                gameSelection.selectedOptions.find((o) => o.id == option.id)
                  .choice
              "
              class="select-width inline-block"
            />
          </div>
          <template v-else>
            <q-toggle
              v-model="findSelectedOption(option.id).value"
              :label="option.name"
            />
          </template>
        </div>
      </template>
    </div>

    <KennerButton
      @click="handleSubmit"
      type="submit"
      push
      color="positive"
      label="Speichern"
      class="q-mt-md"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { useGameSelection } from 'src/composables/gameSelection';

const props = defineProps<{
  leagueId: number
}>()

const {
  gameInformation,
  gameSelection,
  isLoading,
  setGameInformation,
  findChoicesByOption,
  findSelectedOption,
  submitGame,
  platform,
  filter,
  platforms,
  filteredGames,
  loadPlatformsAndGames,
} = useGameSelection(props.leagueId);

const emit = defineEmits(['submit-success']);

const handleSubmit = async () => {
  try {
    await submitGame();
    emit('submit-success');
  } catch (error) {
    console.error('Error submitting game:', error);
  }
};

function getPlatformName(platformId: number | string): string {
  const platformObj = platforms.value.find(p => p.id === platformId);
  return platformObj?.name ?? `ID: ${platformId}`;
}


onMounted(loadPlatformsAndGames);
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

.select-width {
  width: 140px;
}

.hoverable-card {
  transition: background-color 0.3s ease;
  background-color: white;

  &:hover {
    background-color: rgba($secondary, 0.06); // Very light secondary tint
  }
}

</style>

<template>
  <div class="q-pa-md">
    <p class="text-h5">Neues Spiel</p>
    <div class="q-py-md">
      <q-form class="q-gutter-md">
        <kenner-input class="max-w-500" label="Spielname" v-model="name"/>
        <kenner-select class="max-w-500" label="Plattform" :options="platforms" v-model="platform"/>
        <div class="q-mt-xl">
          <div>
            <span class="text-h6">Spieloptionen</span>
            <kenner-button class="q-ml-lg" color="primary" label="" icon="add" @click="addEmptyOption"/>
          </div>
          <div class="flex row ">
            <GameOption
              v-for="gameOption of gameOptions"
              :key="gameOption.internalId"
              :gameOption="gameOption"
            />
          </div>
        </div>
        <kenner-button @click="onSubmit" class="q-my-xl" type="submit" push color="positive" label="Speichern"/>
      </q-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { provide, ref } from 'vue';
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';
import KennerInput from 'components/inputs/KennerInput.vue';
import KennerSelect from 'components/inputs/KennerSelect.vue';
import KennerButton from 'components/buttons/KennerButton.vue';
import { TGameOption } from 'pages/game/models';
import GameOption from 'pages/game/createGame/GameOptionCreate.vue';
import { useCrud } from 'src/composables/crud';
import { useRouter } from 'vue-router';

const router = useRouter()
const $q = useQuasar();

const platforms = ref([ 'BGA', 'Yucata' ]);

const useGameOptions = useCrud<TGameOption>();
const { addItem: addOption, items: gameOptions } = useGameOptions;
provide('useGameOptions', useGameOptions);
let optionCounter = 0;

const name = ref('');
const platform = ref(null);

function addEmptyOption(): void {
  const emptyOption: TGameOption = { title: '', hasChoices: false, internalId: optionCounter, choices: [] };
  addOption(emptyOption);
  optionCounter++;
}

const onSubmit = async () => {
  try {
    const gameId = await createGame();
    await createOptions(gameId);
    $q.notify({
      color: 'positive',
      textColor: 'white',
      icon: 'save',
      message: 'Gespeichert'
    });
    await router.push({ name: 'games' })
  } catch (e) {
    $q.notify({
      color: 'negative',
      textColor: 'white',
      icon: 'warning',
      message: 'Fehler'
    });
  }
};

async function createGame(): Promise<number> {
  try {
    const { data } = await api('games/', {
      method: 'POST',
      data: { name: name.value, platform: platform.value }
    });
    return data.id;
  } catch (e) {
    console.log('Error while creating a new game', e);
    throw new Error('Could not create new game because of following error: ' + e);
  }
}

async function createOptions(gameId: number): Promise<void> {
  for (const option of gameOptions.value) {
    try {
      const { data: newOption } = await api('game-options/', {
        method: 'POST',
        data: {
          name: option.title,
          has_choices: option.hasChoices,
          game: gameId,
        }
      });
      for (const choice of option.choices) {
        api('game-option-choices/', {
          method: 'POST',
          data: {
            name: choice.value,
            option: newOption.id
          }
        });
      }
    } catch (e) {
      console.log('Error creating game options', e);
      throw new Error('Error creating game options: \n' + e);
    }
  }
}
</script>

<style scoped>
.max-w-500 {
  max-width: 500px;
}
</style>

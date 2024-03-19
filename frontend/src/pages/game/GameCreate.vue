<template>
  <div class="q-pa-md">
    <p class="text-h5">Neues Spiel</p>
    <div class="q-py-md">
      <q-form class="q-gutter-md">
        <kenner-input class="max-w-500" label="Spielname" v-model="name" />
        <kenner-select class="max-w-500" label="Plattform" :options="platforms" v-model="platform" />
        <div class="q-mt-xl">
          <div>
            <span class="text-h6">Spieloptionen</span>
            <kenner-button class="q-ml-lg" color="primary" label="" icon="add" @click="addEmptyOption" />
          </div>
          <div class="flex row ">
            <GameOption
              v-for="gameOption of gameOptions"
              :key="gameOption.internalId"
              :gameOption="gameOption"
            />
          </div>
        </div>
        <kenner-button @click="onSubmit" class="q-my-xl" type="submit" push color="positive" label="Speichern" />
      </q-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { provide, ref } from 'vue';
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';
import { useAxios } from '@vueuse/integrations/useAxios';
import KennerInput from 'components/inputs/KennerInput.vue';
import KennerSelect from 'components/inputs/KennerSelect.vue';
import KennerButton from 'components/buttons/KennerButton.vue';
import { TGameOption, TGameOptionChoice } from 'pages/game/models';
import GameOption from 'pages/game/GameOption.vue';
import { useCrud } from 'src/composables/crud';

const $q = useQuasar();

const platforms = ref(['BGA', 'Yucata']);

const useGameOptions = useCrud<TGameOption>();
const { addItem: addOption, items: gameOptions } = useGameOptions;
provide('useGameOptions', useGameOptions);
let optionCounter = 0;

const name = ref('');
const platform = ref(null);

function addEmptyOption(): void {
  const emptyOption: TGameOption = { title: '', isBoolean: true, internalId: optionCounter, choices: [] };
  addOption(emptyOption);
  optionCounter++;
}

const onSubmit = async () => {
  const gameId = await createGame();
  console.log({ gameId });
  // if (isFinished.value) {
  //   $q.notify({
  //     color: 'positive',
  //     textColor: 'white',
  //     icon: 'save',
  //     message: 'Gespeichert'
  //   });
  // } else if (error.value) {
  //   $q.notify({
  //     color: 'negative',
  //     textColor: 'white',
  //     icon: 'warning',
  //     message: 'Fehler'
  //   });
// };
};

async function createGame(): Promise<number> {
  const { response } = await useAxios('games/', {
    method: 'POST',
    data: { name: name.value, platform: platform.value }
  }, api);
  return response.value.data.id;
}

async function createOption(option: TGameOption, gameId: number): Promise<any> {
  return useAxios('game-options/', {
    method: 'POST',
    data: {
      name: option.title,
      game: gameId
    }
  }, api);
}

async function createOptionChoice(choice: TGameOptionChoice, optionId: number): Promise<any> {
  return useAxios('game-option-choices/', {
    method: 'POST',
    data: {
      name: choice.value,
      option: optionId
    }
  }, api);
}

</script>

<style scoped>
.max-w-500 {
  max-width: 500px;
}
</style>

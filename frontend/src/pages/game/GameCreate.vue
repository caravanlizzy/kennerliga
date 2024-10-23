<template>
  <div class="q-pa-md">
    <p class="text-h5">Neues Spiel</p>
    <div class="q-py-md">
      <q-form @submit="onSubmit()" @keydown.enter.stop.prevent class="q-gutter-md">
        <kenner-input class="max-w" label="Spielname" v-model="name"
                      :rules="[val => !!val || 'Bitte wähle einen Spielnamen']"/>
        <kenner-select class="max-w" label="Plattform" :options="platforms" v-model="platform" option-value="name"
                       option-label="name"
                       :rules="[val => !!val || 'Bitte wähle eine Plattform']"/>

        <div class="q-mt-xl q-pa-md">
          <div>
            <span class="text-h6">Spieloptionen</span>
            <kenner-button class="q-ml-lg" color="primary" label="" icon="add" @click="addEmptyOption"/>
          </div>
          <div class="flex row ">
            <game-option
              v-for="gameOption of gameOptions"
              :key="gameOption.itemId"
              :gameOption="gameOption"
            />
          </div>
        </div>
        <create-result-config @update-result-config="updateResultConfig"/>
        <kenner-button class="q-my-xl" type="submit" push color="positive" label="Speichern"/>
      </q-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { provide, Ref, ref } from 'vue';
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';
import KennerInput from 'components/inputs/KennerInput.vue';
import KennerSelect from 'components/inputs/KennerSelect.vue';
import KennerButton from 'components/buttons/KennerButton.vue';
import { TGameOption, TPlatform, TResultConfig } from 'src/models/gameModels';
import GameOption from 'pages/game/createGame/GameOptionCreate.vue';
import { useItemList } from 'src/composables/itemList';
import { useRouter } from 'vue-router';
import CreateResultConfig from 'pages/game/createGame/CreateResultConfig.vue';
import { createGame, createOptions, createResultConfigData } from 'src/services/game/createGameService';
import { createRandomId } from 'src/helper';

const router = useRouter();
const $q = useQuasar();

const { data: platforms } = await api('game/platforms/');

const useGameOptions = useItemList<TGameOption>();
const { addItem: addOption, items: gameOptions } = useGameOptions;
provide('useGameOptions', useGameOptions);

const name = ref('');
const platform: Ref<TPlatform | undefined> = ref(undefined);
const errorMessages: Ref<string[]> = ref([]);

let resultConfig: TResultConfig | undefined = undefined;

function updateResultConfig(newResultConfig: TResultConfig) {
  resultConfig = newResultConfig;
}

function addEmptyOption(): void {
  const emptyOption: TGameOption = { title: '', hasChoices: false, itemId: createRandomId(), choices: [] };
  addOption(emptyOption, { prepend: true });
}


const onSubmit = async () => {
  try {
    if (platform.value === undefined) return;
    const gameId = await createGame(name.value, platform.value);
    await createOptions(gameId, gameOptions.value);
    if (resultConfig !== undefined) {
      await createResultConfigData(gameId, resultConfig);
    } else {
      console.log('Missing result config');
      return;
    }
    $q.notify({
      color: 'positive',
      textColor: 'white',
      icon: 'save',
      message: 'Gespeichert'
    });
    await router.push({ name: 'games' });
  } catch (e) {
    const message = 'Fehler ' + errorMessages.value;
    $q.notify({
      color: 'negative',
      textColor: 'white',
      icon: 'warning',
      message: message
    });
  }
};


</script>

<style scoped>
.max-w {
  max-width: 300px;
}
</style>

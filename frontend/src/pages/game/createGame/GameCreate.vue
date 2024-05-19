<template>
  <div class="q-pa-md">
    <p class="text-h5">Neues Spiel</p>
    <div class="q-py-md">
      <q-form @submit="onSubmit()" class="q-gutter-md">
        <kenner-input class="max-w-500" label="Spielname" v-model="name"
                      :rules="[val => !!val || 'Bitte wähle einen Spielnamen']" />
        <kenner-select class="max-w-500" label="Plattform" :options="platforms" v-model="platform" option-value="name"
                       option-label="name"
                       :rules="[val => !!val || 'Bitte wähle eine Plattform']" />
        {{ gameOptions }}
        <div class="q-mt-xl q-pa-md">
          <div>
            <span class="text-h6">Spieloptionen</span>
            <kenner-button class="q-ml-lg" color="primary" label="" icon="add" @click="addEmptyOption" />
          </div>
          <div class="flex row ">
            <game-option
              v-for="gameOption of gameOptions"
              :key="gameOption.itemId"
              :gameOption="gameOption"
            />
          </div>
        </div>
        <create-result-config @update-result-config="updateResultConfig" />
        <kenner-button class="q-my-xl" type="submit" push color="positive" label="Speichern" />
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
import { TGameOption, TResultConfig } from 'pages/game/models';
import GameOption from 'pages/game/createGame/GameOptionCreate.vue';
import { useItemList } from 'src/composables/itemList';
import { useRouter } from 'vue-router';
import CreateResultConfig from 'pages/game/createGame/CreateResultConfig.vue';

const router = useRouter();
const $q = useQuasar();

const { data: platforms } = await api('game/platforms/');

const useGameOptions = useItemList<TGameOption>();
const { addItem: addOption, items: gameOptions } = useGameOptions;
provide('useGameOptions', useGameOptions);
let optionCounter = 0;

const name = ref('');
const platform = ref(null);
const errorMessages: Ref<string[]> = ref([]);

let resultConfig:TResultConfig|undefined = undefined;
function updateResultConfig(newResultConfig:TResultConfig){
  resultConfig = newResultConfig;
}

const optionIDStorage: { [key: string]: number } = {};

function addItemId(itemId: number, id: number): void {
  optionIDStorage[itemId.toString()] = id;
}

function addEmptyOption(): void {
  const emptyOption: TGameOption = { title: '', hasChoices: false, itemId: optionCounter, choices: [] };
  addOption(emptyOption);
  optionCounter++;
}

async function addRestrictions(option: TGameOption): Promise<void> {
  console.log({ option })
  if (option.onlyIfOption === undefined || option.onlyIfValue === undefined) {
    console.log('No restriction option given');
    return;
  }
  const { onlyIfOption, onlyIfChoice, onlyIfValue } = option;
  const optionId = optionIDStorage[onlyIfOption];
  const choiceId: number | undefined = optionIDStorage[onlyIfChoice];
  const data = { only_if_option: optionId, only_if_value: onlyIfValue, only_if_choice: choiceId };
  if (onlyIfValue) {
    data.only_if_value = onlyIfValue;
  } else {
    data['only_if_choice'] = choiceId;
  }
  await api(`game/options/${optionId}/`, {
    method: 'PATCH',
    data
  });
}

const onSubmit = async () => {
  try {
    const gameId = await createGame();
    await createOptions(gameId);
    await createResultConfigData(gameId);
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
      message: message,
    });
  }
};

async function createGame(): Promise<number> {
  try {
    const { data } = await api('game/games/', {
      method: 'POST',
      data: { name: name.value, platform: platform.value?.id }
    });
    return data.id;
  } catch (e) {
    errorMessages.value.push('CreateGame');
    console.log('Error while creating a new game', e);
    throw new Error('Could not create new game because of following error: ' + e);
  }
}

async function createOptions(gameId: number): Promise<void> {
  for (const option of gameOptions.value) {
    try {
      const { data: newOption } = await api('game/options/', {
        method: 'POST',
        data: {
          name: option.title,
          has_choices: option.hasChoices,
          game: gameId
        }
      });
      addItemId(option.itemId, newOption.id);
      for (const choice of option.choices) {
        await api('game/option-choices/', {
          method: 'POST',
          data: {
            name: choice,
            option: newOption.id
          }
        });
        console.log({ itemIdMap: optionIDStorage });
        // currently not working since list logic has been outsourced
        // addItemId(choice.itemId, data.id);
      }
      await addRestrictions(option);
    } catch (e) {
      errorMessages.value.push('CreateGameOption');
      console.log('Error creating game options', e);
      throw new Error('Error creating game options: \n' + e);
    }
  }
}

async function createResultConfigData(gameId: number): Promise<void> {
  try {
    const {data: resultConfigData} = await api('game/result-configs/', {
      method: 'POST',
      data: {
        game: gameId,
        is_asymmetric: resultConfig?.isAsymmetric,
        has_starting_player_order: resultConfig?.hasStartingPlayerOrder,
        has_points: resultConfig?.hasPoints,
        starting_points_system: resultConfig?.startingPointSystem
      }
    });
    await createFactions(gameId);
    await createTieBreakers(resultConfigData.id);
  } catch (e) {
    errorMessages.value.push('CreateResultConfig');
    console.log('Error creating the result configuration', e);
    throw new Error('Error creating the result configuration: \n' + e);
  }
}

async function createFactions(gameId: number): Promise<void> {
  if(resultConfig === undefined) return;
  if(resultConfig.factions === undefined) return;
  for (const faction of resultConfig.factions){
    try {
      api('game/factions/', {
        method:'POST',
        data: {
          game: gameId,
          name: faction
        }
      })
    } catch(e) {
      console.log('Error creating faction', e)
    }
  }
}

async function createTieBreakers(resultConfigId: number): Promise<void> {
  if(resultConfig === undefined) return;
  if(resultConfig.tieBreakers === undefined) return;
  if(!resultConfig.hasTieBreaker) return;
  for (const [index, tieBreaker] of resultConfig.tieBreakers.entries()){
    try {
      api('game/tie-breakers/', {
        method:'POST',
        data: {
          result_config: resultConfigId,
          name: tieBreaker,
          order: index * 10
        }
      })
    } catch(e) {
      console.log('Error creating tieBreaker', e)
    }
  }
}

</script>

<style scoped>
.max-w-500 {
  max-width: 500px;
}
</style>

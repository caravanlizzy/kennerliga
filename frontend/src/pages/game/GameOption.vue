<template>
  <q-card class=" q-mt-lg column q-mx-md">
    <q-card-section class="row justify-between bg-primary text-white q-pa-md" >
      <div class="">{{gameOption.title}}</div>
      <kenner-button color="accent" size="md" class="close-button q-pa-none" icon="close" @click="deleteOption"></kenner-button>
    </q-card-section>
    <div class="col q-mx-md q-my-xs">
      <q-checkbox color="accent" :model-value="gameOption.isBoolean" @update:model-value="updateBoolean"
                  label="Ja/Nein Option" />
      <kenner-input :model-value="gameOption.title" @update:modelValue="updateTitle" label="Spieloption Titel"
                    class="q-mb-md q-mx-xs" />
      <div v-if="!gameOption.isBoolean" class="column q-pa-xs q-mt-lg">
        <div class="row items-center justify-between ">
          <div class="q-mx-xs text-bold">Auswahloptionen</div>
          <kenner-button icon="add" color="primary" @click="addChoice" dense></kenner-button>
        </div>
        <q-separator class="q-mt-md q-mb-xs" />
        <div v-for="{id, value} of gameOption.choices" :key="id" class="row items-center justify-around">
          <kenner-input :model-value="value" @update:modelValue="updateChoice(id, $event)" label="Auswahloption"
                        class="q-my-md" />
          <kenner-button flat color="accent" icon="delete" class="" @click="removeChoice(id)"></kenner-button>
        </div>

      </div>

    </div>
  </q-card>
</template>

<script setup lang="ts">
import KennerInput from 'components/inputs/KennerInput.vue';
import { TGameOption } from 'pages/game/models';
import KennerButton from 'components/buttons/KennerButton.vue';
import { inject } from 'vue';

const props = defineProps<{ gameOption: TGameOption }>();
const { id: gameId } = props.gameOption;

const { updateItem, deleteItem, createRandomNumber } = inject('useGameOptions');

addChoice();

function updateBoolean(isBoolean) {
  updateItem(gameId, 'isBoolean', isBoolean);
}

function deleteOption() {
  deleteItem(props.gameOption);
}

function updateTitle(newTitle: string) {
  updateItem(gameId, 'title', newTitle);
}

function addChoice() {
  const emptyChoice: TGameOption['choices'] = { id: createRandomNumber(), value: '' };
  updateItem(gameId, 'choices', [...props.gameOption.choices, emptyChoice]);
}

function getChoice(choiceId: number) {
  return props.gameOption.choices.find(choice => choice.id === choiceId);
}

function updateChoice(choiceId: number, newValue: string) {
  const choice = getChoice(choiceId);
  if (choice) {
    choice.value = newValue;
  }
}

function removeChoice(choiceId: number) {
  updateItem(gameId, 'choices', [...props.gameOption.choices.filter(choice => choice.id !== choiceId)]);
}


</script>

<style scoped lang="scss">
.bordered {
  border: 1px solid $primary;
}
.close-button {
  min-width: 22px;
  min-height: 22px;
}
</style>

<template>
  <gameOptionCard>
    <template #cardHeader>
      <div class="">{{gameOption.title}}</div>
      <kenner-button color="accent" size="md" class="close-button q-pa-none" icon="close" @click="deleteOption"></kenner-button>
    </template>
    <template #cardBody>
      <div class="col">
        <q-toggle  color="secondary" :model-value="gameOption.hasChoices" @update:model-value="updateHasChoices"
                   label="Auswahloptionen"/>
        <kenner-input :model-value="gameOption.title" @update:modelValue="updateTitle" label="Spieloption Titel"
                      class="q-mb-md q-mx-xs" />
        <div v-if="gameOption.hasChoices" class="column q-pa-xs q-mt-lg">
          <div class="row items-center justify-between ">
            <div class="q-mx-xs text-bold">Auswahloptionen</div>
            <kenner-button icon="add" color="primary" @click="addChoice" dense></kenner-button>
          </div>
          <q-separator class="q-mt-md q-mb-xs" />
          <div v-for="{internalId, value} of gameOption.choices" :key="internalId" class="row items-center justify-around">
            <kenner-input :model-value="value" @update:modelValue="updateChoice(internalId, $event)" label="Auswahloption"
                          class="q-my-md" />
            <kenner-button flat color="accent" icon="delete" class="" @click="removeChoice(internalId)"></kenner-button>
          </div>
        </div>
      </div>
    </template>
  </gameOptionCard>
</template>

<script setup lang="ts">
import KennerInput from 'components/inputs/KennerInput.vue';
import { TGameOption, TGameOptionChoice } from 'pages/game/models';
import KennerButton from 'components/buttons/KennerButton.vue';
import { inject } from 'vue';
import GameOptionCard from 'components/cards/gameOptionCard.vue';

const props = defineProps<{ gameOption: TGameOption }>();
const { gameOption } = props;

const { updateItem, deleteItem, createRandomNumber } = inject('useGameOptions');

addChoice();

function updateHasChoices(hasChoices) {
  updateItem(gameOption, 'hasChoices', hasChoices);
}

function deleteOption() {
  deleteItem(props.gameOption);
}

function updateTitle(newTitle: string) {
  updateItem(gameOption, 'title', newTitle);
}

function addChoice() {
  const emptyChoice: TGameOption['choices'] = { internalId: createRandomNumber(), value: '' };
  updateItem(gameOption, 'choices', [...props.gameOption.choices, emptyChoice]);
}


function getChoice(choiceId: number):TGameOptionChoice {
  return gameOption.choices.find(choice => choice.internalId === choiceId);
}

function updateChoice(choiceId: number, newValue: string) {
  const choice = getChoice(choiceId);
  if (choice) {
    choice.value = newValue;
  }
}

function removeChoice(choiceId: number) {
  updateItem(gameOption, 'choices', [...props.gameOption.choices.filter(choice => choice.internalId !== choiceId)]);
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

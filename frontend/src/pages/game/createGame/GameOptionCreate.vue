<template>
  <game-option-card>
    <template #cardHeader>
      <div class="">{{ gameOption.title }}</div>
      <kenner-button color="accent" size="md" class="close-button q-pa-none" icon="close"
                     @click="deleteOption"></kenner-button>
    </template>
    <template #cardBody>
      <div class="col">
        <kenner-input :model-value="gameOption.title" @update:modelValue="updateTitle" label="Spieloption Titel"
                      class="q-mb-md q-mx-xs" :rules="[val => !!val || 'Titel erforderlich']" />
        <q-toggle color="secondary" :model-value="gameOption.hasChoices" @update:model-value="updateHasChoices"
                  label="Auswahloptionen" />
        <q-toggle color="accent" label="Bedingungen" :model-value="hasRestrictions"
                  @update:model-value="hasRestrictions = !hasRestrictions; deleteRestriction()" />
        <GameOptionChoiceCreate :addChoice="addChoice" :gameOption="gameOption" v-if="gameOption.hasChoices" />
        <GameOptionRestrictionCreate :gameOption="gameOption" v-if="hasRestrictions" />
      </div>
    </template>
  </game-option-card>
</template>

<script setup lang="ts">
import KennerInput from 'components/inputs/KennerInput.vue';
import { TGameOption } from 'pages/game/models';
import KennerButton from 'components/buttons/KennerButton.vue';
import { inject, ref } from 'vue';
import GameOptionChoiceCreate from 'pages/game/createGame/GameOptionChoiceCreate.vue';
import GameOptionRestrictionCreate from 'pages/game/createGame/GameOptionRestrictionCreate.vue';
import GameOptionCard from 'components/cards/gameOptionCard.vue';

const props = defineProps<{ gameOption: TGameOption }>();
const { gameOption } = props;

const { updateItem, deleteItem, createRandomNumber } = inject('useGameOptions');

const hasRestrictions = ref(false);

addChoice();

function updateHasChoices(hasChoices: boolean) {
  updateItem(gameOption, 'hasChoices', hasChoices);
}

function deleteRestriction(){
  if(!hasRestrictions.value){
    updateItem(gameOption, 'onlyIfOption', undefined);
    updateItem(gameOption, 'onlyIfChoice', undefined);
    updateItem(gameOption, 'onlyIfValue', undefined);
  }
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

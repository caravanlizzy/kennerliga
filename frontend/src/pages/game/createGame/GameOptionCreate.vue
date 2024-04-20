<template>
  <gameOptionCard>
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
                  @update:model-value="hasRestrictions = !hasRestrictions; updateRestriction()" />
        <GameOptionChoiceCreate :gameOption="gameOption" v-if="gameOption.hasChoices" />
        <GameOptionRestrictionCreate :updateRestriction="updateRestriction" :gameOption="gameOption" v-if="hasRestrictions" />
      </div>
    </template>
  </gameOptionCard>
</template>

<script setup lang="ts">
import KennerInput from 'components/inputs/KennerInput.vue';
import { TGameOption, TGameOptionChoice } from 'pages/game/models';
import KennerButton from 'components/buttons/KennerButton.vue';
import { inject, Ref, ref } from 'vue';
import GameOptionChoiceCreate from 'pages/game/createGame/GameOptionChoiceCreate.vue';
import GameOptionRestrictionCreate from 'pages/game/createGame/GameOptionRestrictionCreate.vue';

const props = defineProps<{ gameOption: TGameOption }>();
const { gameOption } = props;

const { updateItem, deleteItem, createRandomNumber, items } = inject('useGameOptions');

interface RestrictionData {
  hasRestrictions: boolean;
  restrictToOption: TGameOption | null;
  restrictionChoice: {
    booleanActive: boolean;
    choiceSelection: {
      value: string | null;
      internalId: string | null;
    };
  };
}

const restrictionInfo: Ref<RestrictionData> = ref({
  hasRestrictions: false,
  restrictToOption: null,
  restrictionChoice: {
    booleanActive: true,
    choiceSelection: {
      value: null,
      internalId: null,
    }
  }
});
const hasRestrictions = ref(false);
const restrictToOption: Ref<TGameOption | null> = ref(null);
const restrictionChoice = ref({ booleanActive: true, choiceSelection: { value: null, internalId: null } });

addChoice();

function updateHasChoices(hasChoices: boolean) {
  updateItem(gameOption, 'hasChoices', hasChoices);
}

function updateRestriction() {
  if (hasRestrictions.value) {
    updateItem(gameOption, 'onlyIfOption', restrictToOption.value?.internalId);
    if (restrictToOption.value?.hasChoices) {
      updateItem(gameOption, 'onlyIfValue', undefined);
      updateItem(gameOption, 'onlyIfChoice', restrictionChoice.value?.choiceSelection.internalId);
    } else {
      updateItem(gameOption, 'onlyIfChoice', undefined);
      updateItem(gameOption, 'onlyIfValue', restrictionChoice.value?.booleanActive);
    }
  } else {
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


function getChoice(choiceId: number): TGameOptionChoice | undefined {
  return gameOption.choices.find(choice => choice.internalId === choiceId);
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

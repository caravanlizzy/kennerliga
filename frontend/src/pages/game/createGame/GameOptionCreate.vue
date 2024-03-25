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
        <div v-if="gameOption.hasChoices" class="column q-pa-xs q-mt-lg">
          <div class="row items-center justify-between ">
            <div class="q-mx-xs text-bold">Auswahloptionen</div>
            <kenner-button icon="add" color="primary" @click="addChoice" dense></kenner-button>
          </div>
          <q-separator class="q-mt-md q-mb-xs" />
          <div v-for="{internalId, value} of gameOption.choices" :key="internalId"
               class="row items-center justify-around">
            <kenner-input :model-value="value" @update:modelValue="updateChoice(internalId, $event)"
                          label="Auswahloption"
                          class="q-my-md"
                          :rules="[val => !!val || 'Auswahl erforderlich']" />

            <kenner-button flat color="accent" icon="delete" class="" @click="removeChoice(internalId)"></kenner-button>
          </div>
        </div>
        <div v-if="hasRestrictions" class="column q-pa-xs q-mt-lg bg-brown-1 q-pa-md">
          <div class="row items-center justify-between ">
            <div class="q-mx-xs text-bold">Bedingung</div>
          </div>
          <q-separator class="q-mt-md q-mb-xs" />
          <kenner-select v-model="restrictToOption" :options="items.filter(item => item.title !== gameOption.title )"
                         class="q-my-md" option-value="title" option-label="title"
                         label="Option" map-options @update:model-value="updateRestriction"
                         :rules="[val => !!val || 'Auswahl erforderlich']"
          />


          <template v-if="restrictToOption && restrictToOption.hasChoices">
            <kenner-select v-model="restrictionChoice.choiceSelection" :options="restrictToOption.choices"
                           class="q-my-md" option-value="value" option-label="value"
                           label="Bedingter Wert" @update:model-value="updateRestriction"
                           :rules="[val => !!val|| 'Auswahl erforderlich']" />
          </template>
          <template v-else-if="restrictToOption && !restrictToOption.hasChoices">
            <q-toggle color="accent" :model-value="restrictionChoice.booleanActive"
                      @update:model-value="restrictionChoice.booleanActive = !restrictionChoice.booleanActive; updateRestriction()"
                      label="Bedingte Option muss aktiv sein" />
          </template>
        </div>
      </div>
    </template>
  </gameOptionCard>
</template>

<script setup lang="ts">
import KennerInput from 'components/inputs/KennerInput.vue';
import { TGameOption, TGameOptionChoice } from 'pages/game/models';
import KennerButton from 'components/buttons/KennerButton.vue';
import { inject, Ref, ref } from 'vue';
import GameOptionCard from 'components/cards/gameOptionCard.vue';
import KennerSelect from 'components/inputs/KennerSelect.vue';

const props = defineProps<{ gameOption: TGameOption }>();
const { gameOption } = props;

const { updateItem, deleteItem, createRandomNumber, items } = inject('useGameOptions');

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

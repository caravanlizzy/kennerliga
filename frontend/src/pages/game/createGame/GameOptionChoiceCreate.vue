<template>
  <div class="column q-pa-xs q-mt-lg">
    <div class="row items-center justify-between ">
      <div class="q-mx-xs text-bold">Auswahloptionen</div>
      <kenner-button icon="add" color="primary" @click="addChoice" dense></kenner-button>
    </div>
    <q-separator class="q-mt-md q-mb-xs"/>
    <div v-for="{itemId, value} of gameOption.choices" :key="itemId"
         class="row items-center justify-around">
      <kenner-input :model-value="value" @update:modelValue="updateChoice(itemId, $event)"
                    label="Auswahloption"
                    class="q-my-md"
                    :rules="[val => !!val || 'Auswahl erforderlich']"/>

      <kenner-button flat dense rounded color="accent" icon="close" class="" @click="removeChoice(itemId)"></kenner-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import KennerButton from 'components/buttons/KennerButton.vue';
import KennerInput from 'components/inputs/KennerInput.vue';
import { TGameOption, TGameOptionChoice } from 'pages/game/models';
import { inject } from 'vue';

const { updateItem } = inject('useGameOptions');
const props = defineProps<{ gameOption: TGameOption, addChoice: () => void }>();

function getChoice(choiceId: number): TGameOptionChoice | undefined {
  return props.gameOption.choices.find(choice => choice.itemId === choiceId);
}

function updateChoice(choiceId: number, newValue: string) {
  const choice = getChoice(choiceId);
  if (choice) {
    choice.value = newValue;
  }
}

function removeChoice(choiceId: number) {
  updateItem(props.gameOption, 'choices', [ ...props.gameOption.choices.filter(choice => choice.itemId !== choiceId) ]);
}
</script>

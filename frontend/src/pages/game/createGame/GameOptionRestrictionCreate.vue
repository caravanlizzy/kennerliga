<template>
  <div class="column q-pa-xs q-mt-lg bg-brown-1 q-pa-md">
    <div class="row items-center justify-between ">
      <div class="q-mx-xs text-bold">Bedingung</div>
    </div>
    <q-separator class="q-mt-md q-mb-xs"/>
    <KennerSelect v-model="restrictToOption" :options="filteredItems"
                   class="q-my-md" option-value="title" option-label="title"
                   label="Option" map-options @update:model-value="updateRestriction"
                   :rules="[val => !!val || 'Auswahl erforderlich']"
    />

    <template v-if="restrictToOption && restrictToOption.hasChoices">
      <KennerSelect v-model="restrictionChoice.choiceSelection" :options="restrictToOption.choices"
                     class="q-my-md" option-value="name" option-label="name"
                     label="Bedingter Wert" @update:model-value="updateRestriction"
                     :rules="[val => !!val|| 'Auswahl erforderlich']"/>
    </template>
    <template v-else-if="restrictToOption && !restrictToOption.hasChoices">
      <q-toggle color="accent" :model-value="restrictionChoice.booleanActive"
                @update:model-value="restrictionChoice.booleanActive = !restrictionChoice.booleanActive; updateRestriction()"
                :label="conditionalLabel"/>
    </template>
  </div>
</template>

<script setup lang="ts">
import KennerSelect from 'components/base/KennerSelect.vue';
import { computed, inject, ref, Ref } from 'vue';
import { TGameOption } from 'src/types';

const props = defineProps<{ gameOption: TGameOption }>();

const { updateItem, items } = inject('useGameOptions');

const restrictToOption: Ref<TGameOption | null> = ref(null);
const restrictionChoice = ref({ booleanActive: true, choiceSelection: { name: null, itemId: null } });

const conditionalLabel = computed(() => restrictionChoice.value.booleanActive ? 'Bedingte Option muss aktiv sein' : 'Bedingte Option muss inaktiv sein')
const filteredItems = computed(() => items.value.filter(item => item.title !== props.gameOption.title));


function updateRestriction() {
  updateItem(props.gameOption, 'onlyIfOption', restrictToOption.value?.itemId);
  if (restrictToOption.value?.hasChoices) {
    updateItem(props.gameOption, 'onlyIfValue', undefined);
    updateItem(props.gameOption, 'onlyIfChoice', restrictionChoice.value?.choiceSelection.itemId);
  } else {
    updateItem(props.gameOption, 'onlyIfChoice', undefined);
    updateItem(props.gameOption, 'onlyIfValue', restrictionChoice.value?.booleanActive);
  }
}
</script>

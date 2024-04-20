<template>
  <div  class="column q-pa-xs q-mt-lg bg-brown-1 q-pa-md">
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
</template>

<script setup lang="ts">
import KennerSelect from 'components/inputs/KennerSelect.vue';
import { TGameOption } from 'pages/game/models';
const props = defineProps<{ gameOption: TGameOption, updateRestriction: }>();
</script>

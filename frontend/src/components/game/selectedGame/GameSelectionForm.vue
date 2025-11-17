<template>
  <div>
    <q-card
      flat
      bordered
      class="q-pa-md q-my-md rounded-borders details-card"
    >
      <q-inner-loading :showing="isLoading">
        <q-spinner-orbit size="96px" color="secondary" />
      </q-inner-loading>

      <template v-if="!isLoading && !gameInformation.game">
        <q-banner class="bg-grey-2 text-grey-8 rounded-borders q-pa-md">
          <div class="row items-center">
            <q-icon name="info" class="q-mr-sm" />
            <div>Please select a game on the left to see details.</div>
          </div>
        </q-banner>
      </template>

      <template v-else-if="gameInformation.game">
        <!-- Header -->
        <div class="row items-center justify-between q-mb-sm">
          <div class="text-h6 text-weight-bold">
            {{ gameInformation.game.name }}
          </div>
          <q-chip
            dense
            square
            outline
            :color="
              getPlatformColor(getPlatformName(platforms, gameInformation.game.platform))
                .color
            "
            :text-color="
              getPlatformColor(getPlatformName(platforms, gameInformation.game.platform))
                .text
            "
          >
            {{ getPlatformName(platforms, gameInformation.game.platform).split('.')[0] }}
          </q-chip>
        </div>

        <q-separator spaced />

        <!-- No settings -->
        <div
          v-if="!gameInformation.options.length"
          class="text-italic text-grey"
        >
          This game has no additional settings.
        </div>

        <!-- Settings -->
        <template v-else>
          <div class="section-title text-grey-7 q-mb-sm">Settings</div>

          <!-- Choices -->
          <div
            v-if="gameInformation.options.some((o) => o.has_choices)"
            class="q-mb-md"
          >
            <div class="row q-col-gutter-md">
              <div
                v-for="option in gameInformation.options.filter(
                  (o) => o.has_choices
                )"
                :key="option.id"
                class="col-12 col-sm-6"
              >
                <KennerSelect
                  :options="findChoicesByOption(option.id)"
                  :label="option.name"
                  option-label="name"
                  dense
                  outlined
                  v-model="
                    gameSelection.selectedOptions.find((o) => o.id == option.id)
                      .choice
                  "
                  :rules="[(val) => !!val || `${option.name} is required`]"
                  class="full-width"
                />
              </div>
            </div>
          </div>

          <!-- Toggles -->
          <div v-if="gameInformation.options.some((o) => !o.has_choices)">
            <div class="section-subtitle q-mb-xs">Toggles</div>
            <div class="row q-col-gutter-sm">
              <q-toggle
                v-for="option in gameInformation.options.filter(
                  (o) => !o.has_choices
                )"
                :key="option.id"
                v-model="findSelectedOption(option.id).value"
                :label="option.name"
                dense
                color="secondary"
                class="col-auto"
              />
            </div>
          </div>
        </template>
      </template>
    </q-card>
    <KennerButton class="float-right" :disable="!isValid" @click="onSubmit()">
      Save
    </KennerButton>
  </div>
</template>
<script setup lang="ts">
import KennerSelect from 'components/base/KennerSelect.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { getPlatformColor, getPlatformName } from 'src/composables/gameSelection';
import { TPlatform } from 'src/models/gameModels';
import { inject } from 'vue';


const platforms = inject<TPlatform[]>('platforms', []);

const props = defineProps<{
  gameInformation: any;
  gameSelection: any;
  isLoading: boolean;
  isValid: boolean;
  onSubmit: () => void;
}>();

function findSelectedOption(optionId: number) {
  // find selected option by game option id
  return props.gameSelection.selectedOptions.find((o) => o.id === optionId);
}

function findChoicesByOption(optionId: number) {
  // get choices for a given option id
  return (
    props.gameInformation.options.find((option) => option.id === optionId)
      ?.choices || null
  );
}
</script>

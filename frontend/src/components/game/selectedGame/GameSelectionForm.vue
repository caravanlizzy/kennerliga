<template>
  <q-card flat class="q-pa-md q-my-md rounded-borders details-card">
    <q-inner-loading v-if="isLoading" :showing="isLoading">
      <q-spinner-orbit size="96px" color="secondary" />
    </q-inner-loading>

    <template v-else>
      <!-- Header -->
      <div class="row items-center justify-between q-mb-sm">
        <div class="text-h6 text-weight-bold text-dark">
          {{ gameInformation.game.name }}
        </div>

        <!-- Right side: platform + save -->
        <div class="row items-center q-gutter-x-md">
          <q-chip
            square
            outline
            class="q-px-sm bg-white"
            :color="
              getPlatformColor(
                getPlatformName(platforms, gameInformation.game.platform)
              ).color
            "
            :text-color="
              getPlatformColor(
                getPlatformName(platforms, gameInformation.game.platform)
              ).text
            "
          >
            {{
              getPlatformName(platforms, gameInformation.game.platform).split(
                '.'
              )[0]
            }}
          </q-chip>

          <KennerButton
            size="md"
            color="accent"
            :disable="!isValid"
            @click="onSubmit"
          >
            Save
          </KennerButton>
        </div>
      </div>

      <q-separator spaced />

      <!-- No settings (use conditional visibility) -->
      <div v-if="!visibleOptionsSafe.length" class="text-italic text-grey">
        This game has no additional settings.
      </div>

      <!-- Settings -->
      <template v-else>
        <div class="section-title text-grey-7 q-mb-sm">Settings</div>

        <!-- Choices -->
        <div
          v-if="visibleOptionsSafe.some((o) => o.has_choices)"
          class="q-mb-md"
        >
          <div class="row q-col-gutter-md">
            <div
              v-for="option in visibleOptionsSafe.filter((o) => o.has_choices)"
              :key="option.id"
              class="col-12 col-sm-6"
            >
              <KennerSelect
                :options="option.choices || null"
                :label="option.name"
                option-label="name"
                color="accent"
                dense
                outlined
                v-model="findSelectedOption(option.id).choice"
                :rules="[(val) => !!val || `${option.name} is required`]"
                class="full-width"
              />
            </div>
          </div>
        </div>

        <!-- Toggles -->
        <div v-if="visibleOptionsSafe.some((o) => !o.has_choices)">
          <div class="section-subtitle q-mb-xs">Toggles</div>
          <div class="row q-col-gutter-sm">
            <q-toggle
              v-for="option in visibleOptionsSafe.filter((o) => !o.has_choices)"
              :key="option.id"
              v-model="findSelectedOption(option.id).value"
              :label="option.name"
              dense
              color="accent"
              class="col-auto"
            />
          </div>
        </div>
      </template>
    </template>
  </q-card>
</template>

<script setup lang="ts">
import KennerSelect from 'components/base/KennerSelect.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { getPlatformColor, getPlatformName } from 'src/composables/gameSelection';
import {
  TPlatform,
  TGameInformation,
  TGameSelection,
  TGameOptionDto,
} from 'src/types';
import { computed, inject } from 'vue';

const platforms = inject<TPlatform[]>('platforms', []);

const props = withDefaults(
  defineProps<{
    gameInformation: TGameInformation;
    gameSelection: TGameSelection;
    isLoading: boolean;
    isValid: boolean;
    onSubmit: () => void;

    // comes from useGameSelection(...).visibleOptions
    visibleOptions?: TGameOptionDto[];
  }>(),
  {
    visibleOptions: () => [],
  }
);

const visibleOptionsSafe = computed(() => props.visibleOptions ?? []);

function findSelectedOption(optionId: number) {
  // find selected option by game option id
  const found = props.gameSelection.selectedOptions.find(
    (o) => o.game_option === optionId
  );
  if (!found) {
    throw new Error(`Selected option not found for optionId: ${optionId}`);
  }
  return found;
}
</script>

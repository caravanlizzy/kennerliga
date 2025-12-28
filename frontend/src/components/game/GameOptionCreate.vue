<template>
  <GameOptionCard>
    <template #content>
      <div class="column q-gutter-sm">

        <!-- Header: title + delete -->
        <div class="row items-start justify-between">
          <KennerInput
            :model-value="gameOption.title"
            @update:modelValue="updateTitle"
            label="Option title"
            class="full-width q-mr-sm"
            :rules="[(val: string) => !!val || 'Title required']"
          />
          <KennerButton
            flat round size="sm" color="negative" icon="delete"
            class="q-mt-xs"
            @click="confirmDelete = true"
          />
          <q-tooltip anchor="bottom middle" self="top middle">Delete option</q-tooltip>
        </div>

        <q-separator spaced />

        <!-- Toggles -->
        <div class="row q-col-gutter-md">
          <div class="col-12 col-sm-6">
            <q-toggle
              :model-value="gameOption.hasChoices"
              @update:model-value="updateHasChoices"
              label="Choices"
              dense
            />
            <div v-if="gameOption.hasChoices" class="text-caption text-grey-7 q-pl-xs q-mt-xs">
              Add selectable values for this option.
            </div>
          </div>

          <div class="col-12 col-sm-6">
            <q-toggle
              label="Conditions"
              :model-value="hasRestrictions"
              @update:model-value="hasRestrictions = !hasRestrictions; deleteRestriction()"
              dense
            />
            <div class="text-caption text-grey-7 q-pl-xs q-mt-xs">
              Only apply this option when another option meets a condition.
            </div>
          </div>
        </div>

        <!-- Choices list -->
        <GameOptionChoiceCreate
          v-if="gameOption.hasChoices"
          :addChoice="addChoice"
          :gameOption="gameOption"
          class="q-mt-sm"
        />

        <!-- Restrictions -->
        <GameOptionRestrictionCreate
          v-if="hasRestrictions"
          :gameOption="gameOption"
          class="q-mt-sm"
        />

        <!-- Empty hint -->
        <div
          v-if="!gameOption.hasChoices && !hasRestrictions"
          class="bg-grey-2 text-grey-8 text-caption q-pa-md rounded-borders"
        >
          Tip: Enable <span class="text-weight-medium">Choices</span> if the option has multiple values,
          and enable <span class="text-weight-medium">Conditions</span> to make this option depend on another.
        </div>
      </div>

      <!-- Delete confirmation -->
      <q-dialog v-model="confirmDelete">
        <q-card class="q-pa-md rounded-borders">
          <div class="text-subtitle1 q-mb-sm">Delete option?</div>
          <div class="text-caption text-grey-7 q-mb-md">This cannot be undone.</div>
          <div class="row justify-end q-gutter-sm">
            <KennerButton flat label="Cancel" v-close-popup />
            <KennerButton color="negative" label="Delete" @click="onConfirmDelete" />
          </div>
        </q-card>
      </q-dialog>
    </template>
  </GameOptionCard>
</template>

<script setup lang="ts">
import KennerInput from 'components/base/KennerInput.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { inject, ref } from 'vue';
import GameOptionChoiceCreate from 'components/game/GameOptionChoiceCreate.vue';
import GameOptionRestrictionCreate from 'components/game/GameOptionRestrictionCreate.vue';
import GameOptionCard from 'components/cards/OverviewCard.vue';
import { createRandomId } from 'src/helpers';
import { TGameOption, TGameOptionChoice } from 'src/types';

const props = defineProps<{ gameOption: TGameOption }>();
const { gameOption } = props;

const { updateItem, deleteItem } = inject('useGameOptions') as any;

// initialize from existing restriction fields if present
const hasRestrictions = ref(Boolean(
  gameOption.onlyIfOption || gameOption.onlyIfChoice || gameOption.onlyIfValue !== undefined
));

const confirmDelete = ref(false);

function updateHasChoices(hasChoices: boolean) {
  updateItem(gameOption, 'hasChoices', hasChoices);
}

function deleteRestriction() {
  if (!hasRestrictions.value) {
    updateItem(gameOption, 'onlyIfOption', undefined);
    updateItem(gameOption, 'onlyIfChoice', undefined);
    updateItem(gameOption, 'onlyIfValue', undefined);
  }
}

function deleteOption() {
  deleteItem(props.gameOption);
}

function onConfirmDelete() {
  confirmDelete.value = false;
  deleteOption();
}

function updateTitle(newTitle: string) {
  updateItem(gameOption, 'title', newTitle);
}

function addChoice() {
  const emptyChoice: TGameOptionChoice = { id: createRandomId(), name: '' };
  updateItem(gameOption, 'choices', [...props.gameOption.choices, emptyChoice]);
}
</script>

<style scoped>
/* Minimal; layout handled via Quasar utility classes */
</style>

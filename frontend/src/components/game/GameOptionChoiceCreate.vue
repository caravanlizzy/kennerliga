<template>
  <div class="column q-pa-xs q-mt-lg">
    <div class="row items-center justify-between q-mx-xs q-mb-xs">
      <div class="text-bold">Choices</div>
      <q-badge transparent class="text-caption"
        >{{ choiceCount }} total</q-badge
      >
    </div>

    <!-- If ListCreator supports initial values, pass them in -->
    <ListCreator
      class="q-mx-xs"
      button-label="New option"
      :initial="initialNames"
      @update-list="onUpdate"
    />

    <div v-if="!choiceCount" class="text-caption text-grey-7 q-mx-xs q-mt-sm">
      Tip: Add at least one choice if this option should present a selection.
    </div>
  </div>
</template>

<script setup lang="ts">
import { inject, computed } from 'vue';
import ListCreator from 'components/lists/ListCreator.vue';
import { TGameOption, TGameOptionChoice } from 'src/types';
import { createRandomId } from 'src/helpers';

const { updateItem } = inject('useGameOptions') as {
  updateItem: (
    item: TGameOption,
    key: keyof TGameOption,
    value: TGameOption[keyof TGameOption]
  ) => void;
};

const props = defineProps<{ gameOption: TGameOption }>();

const initialNames = computed<string[]>(() =>
  (props.gameOption.choices || []).map((c) => c.name)
);
const choiceCount = computed(() => props.gameOption.choices?.length ?? 0);

/**
 * Map ListCreator's string[] to TGameOptionChoice[] while keeping stable IDs.
 */
function onUpdate(updatedNames: string[]) {
  const existingByName = new Map(
    (props.gameOption.choices || []).map((c) => [c.name, c.id])
  );

  const nextChoices: TGameOptionChoice[] = updatedNames.map((name, i) => ({
    id:
      existingByName.get(name) ??
      props.gameOption.choices?.[i]?.id ??
      createRandomId(),
    name,
  }));

  updateItem(props.gameOption, 'choices', nextChoices);
}
</script>

<template>
  <div class="column q-pa-md q-mt-md bg-grey-2 rounded-borders">
    <!-- Header -->
    <div class="row items-center justify-between q-mb-xs">
      <div class="text-subtitle2 text-weight-medium">Condition</div>
      <KennerButton
        flat dense size="sm" icon="restart_alt" label="Clear"
        :disable="!restrictToOption"
        @click="clearRestriction"
      />
    </div>
    <div class="text-caption text-grey-7 q-mb-sm">
      Make this option depend on another option or a specific choice.
    </div>

    <q-separator spaced />

    <!-- Pick the option to depend on -->
    <KennerSelect
      v-model="restrictToOption"
      :options="filteredItems"
      class="q-my-sm"
      option-value="title"
      option-label="title"
      label="Option"
      map-options
      @update:model-value="updateRestriction"
      :rules="[(val: string) => !!val || 'Selection required']"
    />

    <div v-if="restrictToOption" class="row items-center q-gutter-xs q-pl-xs q-mb-sm">
      <q-badge outline class="text-caption text-dark">
        {{ restrictToOption.hasChoices ? 'Choice-based' : 'Boolean' }}
      </q-badge>
    </div>

    <!-- Choice-based condition -->
    <div v-if="restrictToOption && restrictToOption.hasChoices">
      <KennerSelect
        v-model="restrictionChoice.choiceSelection"
        :options="restrictToOption.choices"
        class="q-my-sm"
        option-value="name"
        option-label="name"
        label="Conditional value"
        map-options
        @update:model-value="updateRestriction"
        :rules="[(val: string) => !!val || 'Selection required']"
      />
      <div class="text-caption text-grey-7 q-pl-xs">
        Applies only if the selected option equals this value.
      </div>
    </div>

    <!-- Boolean condition -->
    <div v-else-if="restrictToOption">
      <q-toggle
        color="accent" dense
        :model-value="restrictionChoice.booleanActive"
        @update:model-value="restrictionChoice.booleanActive = !restrictionChoice.booleanActive; updateRestriction()"
        :label="conditionalLabel"
        class="q-mt-xs"
      />
      <div class="text-caption text-grey-7 q-pl-xs q-mt-xs">
        Applies only if the selected option is {{ restrictionChoice.booleanActive ? 'active' : 'inactive' }}.
      </div>
    </div>

    <!-- Empty helper -->
    <div v-else class="text-caption text-grey-6 q-pt-sm">
      Choose an option above to define a condition.
    </div>
  </div>
</template>

<script setup lang="ts">
import KennerSelect from 'components/base/KennerSelect.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { computed, inject, ref, Ref } from 'vue';
import { TGameOption } from 'src/types';

const props = defineProps<{ gameOption: TGameOption }>();
const { updateItem, items } = inject('useGameOptions') as {
  updateItem: (item: TGameOption, key: keyof TGameOption, value: any) => void;
  items: Ref<TGameOption[]>;
};

const restrictToOption: Ref<TGameOption | null> = ref(null);
const restrictionChoice = ref({
  booleanActive: true,
  choiceSelection: { name: null as string | null, id: null as any }
});

const conditionalLabel = computed(() =>
  restrictionChoice.value.booleanActive
    ? 'Conditional option must be active'
    : 'Conditional option must be inactive'
);

const filteredItems = computed(() =>
  items.value.filter(item => item.title !== props.gameOption.title)
);

function updateRestriction() {
  updateItem(props.gameOption, 'onlyIfOption', restrictToOption.value?.id);
  if (restrictToOption.value?.hasChoices) {
    updateItem(props.gameOption, 'onlyIfValue', undefined);
    updateItem(props.gameOption, 'onlyIfChoice', restrictionChoice.value?.choiceSelection.id);
  } else {
    updateItem(props.gameOption, 'onlyIfChoice', undefined);
    updateItem(props.gameOption, 'onlyIfValue', restrictionChoice.value?.booleanActive);
  }
}

// Quick reset (UI sugar only; logic unchanged)
function clearRestriction() {
  restrictToOption.value = null;
  restrictionChoice.value = { booleanActive: true, choiceSelection: { name: null, id: null } };
  updateItem(props.gameOption, 'onlyIfOption', undefined);
  updateItem(props.gameOption, 'onlyIfChoice', undefined);
  updateItem(props.gameOption, 'onlyIfValue', undefined);
}
</script>

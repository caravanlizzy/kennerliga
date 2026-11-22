<template>
  <q-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <q-card
      style="
        min-width: 320px;
        max-width: 480px;
        width: 100%;
        border-radius: 16px;
      "
      class="q-pa-md"
    >
      <q-card-section class="row items-center justify-between q-pb-none">
        <div class="text-subtitle1 text-weight-bold">Add Participant</div>
        <KennerButton
          v-close-popup
          icon="close"
          flat
          round
          dense
          color="grey-6"
          aria-label="Close"
        />
      </q-card-section>

      <q-card-section class="q-pt-sm">
        <p class="text-caption text-grey-7 q-mb-md">
          Select a player to register for {{ seasonName }}.
        </p>

        <ErrorDisplay v-if="error" :error="error" class="q-mb-sm" />

        <KennerSelect
          v-model="selectedProfileId"
          :options="filteredOptions"
          label="Select player profile"
          option-label="label"
          option-value="value"
          emit-value
          map-options
          use-input
          input-debounce="0"
          @filter="filterProfiles"
        >
          <template #no-option>
            <q-item>
              <q-item-section class="text-grey">
                No matching players available
              </q-item-section>
            </q-item>
          </template>
        </KennerSelect>
      </q-card-section>

      <q-card-actions align="right" class="q-pt-md">
        <KennerButton
          flat
          no-caps
          label="Cancel"
          color="grey-7"
          v-close-popup
        />
        <KennerButton
          no-caps
          label="Add Player"
          color="primary"
          :loading="loading"
          :disable="!selectedProfileId"
          @click="onAdd"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import ErrorDisplay from 'components/base/ErrorDisplay.vue';

const props = defineProps<{
  modelValue: boolean;
  seasonName?: string;
  loading: boolean;
  error: string | null;
  profileOptions: { label: string; value: number }[];
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void;
  (e: 'add', profileId: number): void;
}>();

const selectedProfileId = ref<number | null>(null);
const filteredOptions = ref<{ label: string; value: number }[]>([]);

watch(
  () => props.profileOptions,
  (options) => {
    filteredOptions.value = options;
  },
  { immediate: true }
);

watch(
  () => props.modelValue,
  (open) => {
    if (open) {
      selectedProfileId.value = null;
      filteredOptions.value = props.profileOptions;
    }
  }
);

function filterProfiles(val: string, update: (callbackFn: () => void) => void) {
  update(() => {
    const needle = val.toLowerCase().trim();
    if (!needle) {
      filteredOptions.value = props.profileOptions;
    } else {
      filteredOptions.value = props.profileOptions.filter((v) =>
        v.label.toLowerCase().includes(needle)
      );
    }
  });
}

function onAdd() {
  if (selectedProfileId.value) {
    emit('add', selectedProfileId.value);
  }
}
</script>

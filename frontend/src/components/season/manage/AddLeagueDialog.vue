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
        <div class="text-subtitle1 text-weight-bold">Add League</div>
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

      <q-card-section class="q-pt-sm column q-gutter-y-sm">
        <p class="text-caption text-grey-7 q-mb-xs">
          Create a new league for {{ seasonName }}.
        </p>

        <ErrorDisplay v-if="error" :error="error" class="q-mb-sm" />

        <KennerInput
          v-model.number="level"
          type="number"
          label="League Level (e.g. 1)"
        />

        <KennerSelect
          v-model="memberIds"
          :options="participantOptions"
          label="Select participants (optional)"
          option-label="label"
          option-value="value"
          emit-value
          map-options
          multiple
          use-chips
        >
          <template #no-option>
            <q-item>
              <q-item-section class="text-grey">
                No unassigned participants available
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
          label="Create League"
          color="accent"
          :loading="loading"
          :disable="!level"
          @click="onCreate"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerInput from 'components/base/KennerInput.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import ErrorDisplay from 'components/base/ErrorDisplay.vue';

const props = defineProps<{
  modelValue: boolean;
  seasonName?: string;
  loading: boolean;
  error: string | null;
  initialLevel: number;
  participantOptions: { label: string; value: number }[];
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void;
  (e: 'create', payload: { level: number; member_ids: number[] }): void;
}>();

const level = ref<number>(1);
const memberIds = ref<number[]>([]);

watch(
  () => props.initialLevel,
  (val) => {
    level.value = val;
  },
  { immediate: true }
);

watch(
  () => props.modelValue,
  (open) => {
    if (open) {
      level.value = props.initialLevel;
      memberIds.value = [];
    }
  }
);

function onCreate() {
  if (level.value) {
    emit('create', {
      level: level.value,
      member_ids: memberIds.value,
    });
  }
}
</script>

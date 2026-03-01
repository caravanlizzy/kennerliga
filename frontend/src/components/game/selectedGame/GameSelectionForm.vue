<template>
  <q-card flat class="q-pa-sm modern-details-card">
    <q-inner-loading v-if="isLoading" :showing="isLoading" class="rounded-borders">
      <q-spinner-grid size="4em" color="primary" />
    </q-inner-loading>

    <template v-else>
      <!-- Header -->
      <div class="column q-mb-md q-pa-md">
        <!-- Platform info -->
        <div class="row items-center q-gutter-x-sm q-mb-xs">
          <q-badge
            rounded
            :color="getPlatformColor(getPlatformName(platforms, gameInformation.game.platform)).color"
            style="width: 10px; height: 10px; padding: 0"
          />
          <span class="text-overline text-grey-7 font-weight-700 letter-spacing-1">
            {{ getPlatformName(platforms, gameInformation.game.platform).split('.')[0] }}
          </span>
        </div>

        <!-- Title and Button Row -->
        <div class="row items-center justify-between no-wrap q-gutter-x-lg">
          <div class="text-h6 text-weight-bolder text-dark line-height-1">
            {{ gameInformation.game.name }}
          </div>

          <div class="flex-shrink-0">
            <KennerButton
              size="md"
              color="primary"
              icon="save"
              :disable="!isValid"
              @click="onSubmit"
              class="shadow-4 save-btn"
            >
              Confirm Selection
            </KennerButton>
          </div>
        </div>
      </div>

      <q-separator class="q-mb-md opacity-10" />

      <!-- No settings (use conditional visibility) -->
      <div v-if="!visibleOptionsSafe.length" class="text-center q-pa-md bg-blue-grey-1 rounded-borders border-subtle">
        <q-icon name="info" size="xs" color="grey-5" class="q-mb-xs" />
        <div class="text-caption text-grey-7 font-weight-500">
          No additional settings for this game.
        </div>
      </div>

      <!-- Settings -->
      <template v-else>
        <div class="row items-center q-gutter-x-sm q-mb-md">
          <q-icon name="settings" size="18px" color="primary" />
          <div class="text-subtitle2 text-weight-bold text-uppercase letter-spacing-1 text-primary">Game Settings</div>
        </div>

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
                v-model="findSelectedOption(option.id).choice"
                :rules="[(val) => !!val || `${option.name} is required`]"
                class="full-width"
              />
            </div>
          </div>
        </div>

        <!-- Toggles -->
        <div v-if="visibleOptionsSafe.some((o) => !o.has_choices)" class="bg-blue-grey-1 q-pa-md rounded-borders border-subtle">
          <div class="text-caption text-weight-bold text-grey-7 text-uppercase q-mb-sm letter-spacing-1">Toggles</div>
          <div class="row q-col-gutter-sm">
            <div
              v-for="option in visibleOptionsSafe.filter((o) => !o.has_choices)"
              :key="option.id"
              class="col-auto"
            >
              <q-toggle
                v-model="findSelectedOption(option.id).value"
                :label="option.name"
                dense
                color="primary"
                class="font-weight-600"
              />
            </div>
          </div>
        </div>
      </template>
    </template>
  </q-card>
</template>

<style lang="scss" scoped>
.modern-details-card {
  border-radius: 16px;
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
}

.line-height-1 {
  line-height: 1.1;
}

.letter-spacing-1 {
  letter-spacing: 0.05em;
}

.save-btn {
  transition: all 0.3s ease;
  &:not(.q-btn--disabled) {
    animation: pulse-btn 2s infinite;
  }
}

@keyframes pulse-btn {
  0% { box-shadow: 0 0 0 0 rgba(54, 64, 88, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(54, 64, 88, 0); }
  100% { box-shadow: 0 0 0 0 rgba(54, 64, 88, 0); }
}

.font-weight-500 {
  font-weight: 500;
}

.font-weight-600 {
  font-weight: 600;
}

.flex-shrink-0 {
  flex-shrink: 0;
}

.opacity-10 {
  opacity: 0.1;
}

.border-subtle {
  border: 1px solid rgba(0, 0, 0, 0.05);
}
</style>

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
    // If we can't find it, we should return a dummy object to avoid crashing
    // instead of throwing an error. This can happen if props are out of sync.
    return { value: false, choice: null };
  }
  return found;
}
</script>

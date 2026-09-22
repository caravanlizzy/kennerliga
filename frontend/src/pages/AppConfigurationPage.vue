<template>
  <q-page class="q-py-md flex justify-center">
    <div style="max-width: var(--kenner-max-width-text); width: 100%" class="q-px-sm">
      <!-- Header -->
      <div class="management-hero-card q-pa-lg q-mb-lg row items-center justify-between">
        <div class="column">
          <div class="row items-center q-gutter-x-sm q-mb-xs">
            <q-icon name="tune" color="primary" size="32px" />
            <div class="text-h5 text-weight-bold text-dark tracking-tight">
              App Configuration
            </div>
          </div>
          <div class="text-caption text-grey-7">
            Manage annual game constraints and tiebreaker decider rules.
          </div>
        </div>
      </div>

      <LoadingSpinner v-if="loading" />

      <template v-else>
        <!-- Edit current configuration -->
        <q-card flat class="management-card q-mb-lg">
          <q-card-section class="q-pa-lg">
            <div class="text-subtitle1 text-weight-bold q-mb-md text-dark row items-center q-gutter-x-xs">
              <q-icon name="settings_suggest" color="primary" size="20px" />
              <span>Current Settings</span>
            </div>

            <q-form @submit.prevent="submit" class="q-gutter-y-md">
              <KennerInput
                v-model.number="form.max_same_game_per_year"
                label="Max same game per year"
                type="number"
                :rules="[
                  (val) => (val !== null && val !== '') || 'A limit is required',
                  (val) => Number(val) >= 1 || 'Must be at least 1',
                ]"
              />

              <div>
                <KennerSelect
                  v-model="form.tie_decider_game"
                  :options="gameOptions"
                  label="Tie-decider game"
                  emit-value
                  map-options
                  clearable
                />
                <div class="text-caption text-grey-6 q-mt-xs">
                  The game played to decide a league when a tie has to be broken.
                </div>
              </div>

              <div class="row justify-end q-mt-md">
                <KennerButton icon="save" type="submit" color="primary">
                  Save Configuration
                </KennerButton>
              </div>
            </q-form>
          </q-card-section>
        </q-card>

        <!-- Change history -->
        <q-card flat class="management-card">
          <q-card-section class="q-pa-lg">
            <div class="text-subtitle1 text-weight-bold q-mb-md text-dark row items-center justify-between">
              <div class="row items-center q-gutter-x-xs">
                <q-icon name="manage_history" color="primary" size="20px" />
                <span>Change History</span>
              </div>
              <q-badge color="primary" rounded class="q-px-sm">
                {{ history.length }}
              </q-badge>
            </div>

            <div v-if="history.length === 0" class="text-center text-grey-6 q-pa-xl column items-center">
              <q-icon name="manage_history" size="48px" class="opacity-30 q-mb-sm" />
              <span>No configuration history recorded yet</span>
            </div>

            <div v-else class="column q-gutter-y-sm">
              <div
                v-for="entry in history"
                :key="entry.id"
                class="history-item q-pa-md rounded-borders bg-grey-1"
              >
                <div class="row items-center justify-between">
                  <span class="text-body2 text-weight-bold text-dark">
                    Max same game / year: {{ entry.max_same_game_per_year }}
                  </span>
                  <q-chip dense outline color="primary" icon="sports_esports" size="sm">
                    Tie-decider: {{ entry.tie_decider_game_name ?? 'None' }}
                  </q-chip>
                </div>
                <div class="text-caption text-grey-6 q-mt-xs">
                  {{ formatDate(entry.created_at) }}
                  <template v-if="entry.created_by_username">
                    · by <span class="text-weight-medium">{{ entry.created_by_username }}</span>
                  </template>
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </template>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { useQuasar } from 'quasar';
import { useConfigurationStore } from 'stores/configurationStore';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import KennerInput from 'components/base/KennerInput.vue';
import { AppConfigurationCreate } from 'src/types';

defineOptions({ name: 'AppConfigurationPage' });

const $q = useQuasar();

const configurationStore = useConfigurationStore();
const { current, history, games, loading } = storeToRefs(configurationStore);
const { init, saveConfiguration } = configurationStore;

const form = reactive<AppConfigurationCreate>({
  max_same_game_per_year: 2,
  tie_decider_game: null,
});

const gameOptions = computed(() =>
  games.value.map((game) => ({ label: game.name, value: game.id })),
);

function applyCurrent() {
  if (current.value) {
    form.max_same_game_per_year = current.value.max_same_game_per_year;
    form.tie_decider_game = current.value.tie_decider_game;
  }
}

// Prefill the form once the current configuration finishes loading.
watch(current, applyCurrent, { immediate: true });

function formatDate(value: string): string {
  return new Date(value).toLocaleString();
}

async function submit() {
  try {
    await saveConfiguration({ ...form });
    $q.notify({ type: 'positive', message: 'Configuration saved' });
  } catch (e) {
    console.error('Error saving configuration:', e);
    $q.notify({ type: 'negative', message: 'Failed to save configuration' });
  }
}

onMounted(() => {
  void init();
});
</script>

<style scoped lang="scss">
.management-hero-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--kenner-border-color, rgba(0, 0, 0, 0.08));
  border-radius: var(--kenner-card-radius, 16px);
}

.management-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--kenner-border-color, rgba(0, 0, 0, 0.08));
  border-radius: var(--kenner-card-radius, 16px);
}

.history-item {
  border: 1px solid rgba(0, 0, 0, 0.05);
}
</style>

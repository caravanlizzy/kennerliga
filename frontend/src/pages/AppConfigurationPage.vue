<template>
  <q-page class="q-pa-md">
    <div class="text-h4 q-mb-lg">App Configuration</div>

    <LoadingSpinner v-if="loading" />

    <template v-else>
      <!-- Edit current configuration -->
      <q-card flat bordered class="q-mb-lg">
        <q-card-section>
          <div class="text-h6 q-mb-md">Current Settings</div>

          <q-form @submit.prevent="submit" class="q-gutter-md">
            <KennerInput
              v-model.number="form.max_same_game_per_year"
              label="Max same game per year"
              type="number"
              :rules="[
                (val) => (val !== null && val !== '') || 'A limit is required',
                (val) => Number(val) >= 1 || 'Must be at least 1',
              ]"
            />

            <KennerSelect
              v-model="form.tie_decider_game"
              :options="gameOptions"
              label="Tie-decider game"
              emit-value
              map-options
              clearable
            />
            <div class="text-caption text-grey-7">
              The game played to decide a league when a tie has to be broken.
            </div>

            <div class="row justify-end">
              <KennerButton icon="save" type="submit">
                Save Configuration
              </KennerButton>
            </div>
          </q-form>
        </q-card-section>
      </q-card>

      <!-- Change history -->
      <q-card flat bordered>
        <q-card-section>
          <div class="text-h6 q-mb-md">Change History</div>

          <div v-if="history.length === 0" class="text-center text-grey q-pa-lg">
            No configuration saved yet
          </div>

          <q-list v-else separator>
            <q-item v-for="entry in history" :key="entry.id">
              <q-item-section>
                <q-item-label>
                  Max same game per year: {{ entry.max_same_game_per_year }}
                </q-item-label>
                <q-item-label>
                  Tie-decider game: {{ entry.tie_decider_game_name ?? '—' }}
                </q-item-label>
                <q-item-label caption>
                  {{ formatDate(entry.created_at) }}
                  <template v-if="entry.created_by_username">
                    · by {{ entry.created_by_username }}
                  </template>
                </q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
      </q-card>
    </template>
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

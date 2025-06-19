<template>
  <div class="q-pa-md">
    <q-form v-if="formData.length" @submit.prevent="submitResults">
      <div class="row q-col-gutter-md q-mb-lg">
        <div
          v-for="(player, index) in players"
          :key="player.id"
          class="col-12 col-md-6 col-lg-4"
        >
          <q-card flat bordered class="q-pa-md shadow-1 rounded-borders">
            <div class="text-h6 text-bold text-primary q-mb-sm">
              {{ player.username }}
            </div>

            <div class="row q-col-gutter-sm">
              <div v-if="resultConfig?.has_points" class="col-12">
                <q-input
                  v-model.number="formData[index].points"
                  type="number"
                  label="Punkte"
                  dense
                  outlined
                  :rules="[(val) => val !== null || 'Pflichtfeld']"
                />
              </div>

              <div
                v-if="resultConfig?.has_starting_player_order"
                class="col-12"
              >
                <q-input
                  v-model.number="formData[index].starting_position"
                  type="number"
                  label="Startposition"
                  dense
                  outlined
                />
              </div>

              <div v-if="resultConfig?.is_asymmetric" class="col-12">
                <q-select
                  v-model="formData[index].faction_id"
                  :options="factions"
                  option-label="name"
                  option-value="id"
                  label="Faction"
                  dense
                  outlined
                />
              </div>

              <div v-if="tieBreakerRequired" class="col-12">
                <q-input
                  v-model="formData[index].tie_breaker_value"
                  label="Tie-Breaker Wert"
                  dense
                  outlined
                />
              </div>
            </div>
          </q-card>
        </div>
      </div>

      <div class="q-mt-lg row justify-end">
        <q-btn
          type="submit"
          label="Ergebnisse speichern"
          color="primary"
          unelevated
        />
      </div>
    </q-form>

    <q-spinner v-else color="primary" size="md" class="q-my-xl" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import { api } from 'boot/axios';
import { useQuasar } from 'quasar';

const $q = useQuasar();

const props = defineProps<{
  selectedGameId: number;
  players: Array<{ id: number; username: string }>;
}>();

const resultConfig = ref<any>(null);
const factions = ref<Array<{ id: number; name: string }>>([]);
const formData = ref<Array<any>>([]);
const tieBreakerRequired = ref(false);

async function fetchResultConfig() {
  const { data: selectedGame } = await api.get(`game/selected-games/${props.selectedGameId}/`);
  const gameId = selectedGame.game;

  if (!gameId) {
    console.warn('Game ID not found');
    return;
  }

  const { data } = await api.get(`game/result-configs/?game=${gameId}`);
  resultConfig.value = data[0];
}



async function fetchFactions() {
  const { data } = await api.get(`game/selected-games/${props.selectedGameId}/`);
  const gameId = data.game; // assuming the API returns something like { game: 3, ... }

  const factionRes = await api.get(`game/factions/?game=${gameId}`);
  factions.value = factionRes.data;
}

function resetFormData() {
  formData.value = props.players.map((p) => ({
    player_profile: p.id,
    selected_game: props.selectedGameId,
    points: null,
    starting_position: null,
    faction_id: null,
    tie_breaker_value: '',
  }));
  tieBreakerRequired.value = false;
}

watch(
  () => props.selectedGameId,
  async () => {
    if (props.selectedGameId) {
      await fetchResultConfig();
      await fetchFactions();
      resetFormData();
    }
  },
  { immediate: true }
);

async function submitResults() {
  // Sanitize faction_id fields
  formData.value = formData.value.map((entry) => ({
    ...entry,
    faction_id:
      typeof entry.faction_id === 'object'
        ? entry.faction_id.id
        : entry.faction_id,
  }));
  const payload = {
    selected_game: props.selectedGameId,
    results: formData.value,
    dry_run: true,
  };

  try {
    const dryRunResponse = await api.post('/result/match-results/', payload);

    if (dryRunResponse.status === 200) {
      const confirmed = await $q.dialog({
        title: 'Ergebnisse speichern',
        message: 'Dry-Run erfolgreich. Ergebnisse jetzt speichern?',
        cancel: true,
        ok: {
          label: 'Speichern',
          color: 'primary',
        },
        persistent: true,
      });

      if (confirmed) {
        const finalPayload = { ...payload };
        delete finalPayload.dry_run;
        await api.post('/result/match-results/', finalPayload);
        $q.notify({
          type: 'positive',
          message: 'Ergebnisse erfolgreich gespeichert!',
        });
        resetFormData(); // ✅ only reset after real submission
      }
    }
  } catch (err: any) {
    if (err.response?.status === 202) {
      tieBreakerRequired.value = true;
      const tied = err.response.data?.tied_players?.join(', ') || 'Unbekannt';
      $q.notify({
        type: 'warning',
        message: `Unentschieden erkannt zwischen Spielern: ${tied}. Bitte Tie-Breaker Werte eingeben.`,
      });
    } else if (err.response?.data?.detail) {
      $q.notify({ type: 'negative', message: err.response.data.detail });
    } else {
      console.error('Fehler beim Senden:', err);
      $q.notify({
        type: 'negative',
        message: 'Unbekannter Fehler beim Speichern.',
      });
    }
  }
}

</script>

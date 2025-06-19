<template>
  <div class="q-pa-md">
    <q-form @submit.prevent="submitResults" v-if="formData.length">
      <div v-for="(player, index) in players" :key="player.id" class="q-mb-md">
        <q-card flat bordered class="q-pa-md">
          <div class="text-subtitle1 text-bold">{{ player.username }}</div>

          <q-input
            v-if="resultConfig?.has_points"
            v-model.number="formData[index].points"
            type="number"
            label="Punkte"
            dense
            outlined
            class="q-mt-sm"
            :rules="[val => val !== null || 'Pflichtfeld']"
          />

          <q-input
            v-if="resultConfig?.has_starting_player_order"
            v-model.number="formData[index].starting_position"
            type="number"
            label="Startposition"
            dense
            outlined
            class="q-mt-sm"
          />

          <q-select
            v-if="resultConfig?.is_asymmetric"
            v-model="formData[index].faction_id"
            :options="factions"
            option-label="name"
            option-value="id"
            label="Fraktion"
            dense
            outlined
            class="q-mt-sm"
          />

          <q-input
            v-model="formData[index].tie_breaker_value"
            label="Tiebreaker-Wert"
            dense
            outlined
            class="q-mt-sm"
          />
        </q-card>
      </div>

      <q-btn type="submit" label="Ergebnisse testen & speichern" color="primary" />
    </q-form>
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

async function fetchResultConfig() {
  const { data } = await api.get(`game/result-configs/?game=${props.selectedGameId}`);
  resultConfig.value = data[0]; // assuming one ResultConfig per game
}

async function fetchFactions() {
  const { data } = await api.get('game/factions/'); // adapt to your actual endpoint
  factions.value = data;
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
}

// Re-fetch config and reset form when selectedGameId changes
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
  const payload = {
    selected_game: props.selectedGameId,
    results: formData.value,
    dry_run: true,
  };

  try {
    // Step 1: Dry-run request
    const dryRunResponse = await api.post('/result/match-results/', payload);

    if (dryRunResponse.status === 200) {
      const confirmed = await $q.dialog({
        title: 'Ergebnisse speichern',
        message: 'Dry-run erfolgreich. Möchtest du die Ergebnisse speichern?',
        cancel: true,
        persistent: true,
      });

      if (confirmed) {
        // Step 2: Final save without dry_run
        const savePayload = { ...payload };
        delete savePayload.dry_run;

        await api.post('/result/match-results/', savePayload);
        $q.notify({ type: 'positive', message: 'Ergebnisse erfolgreich gespeichert!' });
      }
    }
  } catch (err: any) {
    if (err.response?.status === 202) {
      const tied = err.response.data?.tied_players?.join(', ') || 'Unbekannt';
      $q.notify({
        type: 'warning',
        message: `Unentschieden erkannt zwischen Spielern: ${tied}. Bitte Tie-Breaker-Werte prüfen.`,
      });
    } else if (err.response?.data?.detail) {
      $q.notify({ type: 'negative', message: err.response.data.detail });
    } else {
      console.error('Fehler beim Senden:', err);
      $q.notify({ type: 'negative', message: 'Unbekannter Fehler beim Speichern.' });
    }
  }
}
</script>

<template>
  <q-card class="q-pa-md" flat bordered rounded>
    <div class="row items-center q-mb-md">
      <div class="col">
        <div class="text-h6 text-primary">Match Result</div>
      </div>
      <div class="col-auto">
        <q-toggle
          v-model="orderByStartingPos"
          label="Order by starting position"
          color="secondary"
          dense
        />
      </div>
    </div>

    <div class="q-pa-md">
      <q-form v-if="formData.length" @submit.prevent="submitResults">
        <div class="row q-col-gutter-md q-mb-xl">
          <div
            v-for="member in displayMembers"
            :key="member.id"
            class="col-12 col-sm-6 col-md-4 col-lg-3"
          >
            <q-card flat class="sandy-background text-primary rounded-borders">
              <q-card-section
                class="form-card-header text-subtitle2 text-center"
              >
                {{ member.username }}
              </q-card-section>

              <q-separator />

              <q-card-section class="q-gutter-md">
                <KennerInput
                  v-if="resultConfig?.has_points"
                  v-model.number="getEntry(member.id).points"
                  type="number"
                  inputmode="numeric"
                  label="Points"
                  dense
                  outlined
                  :rules="[(val:string) => val !== null || 'Pflichtfeld']"
                />

                <!-- Starting position -->
                <div class="text-caption text-weight-medium q-mt-xs row items-center justify-between">
                  <div>
                    Starting position
                  </div>
                  <div>
                    <q-btn-group flat class="q-gutter-x-xs">
                      <q-btn
                        v-for="pos in members.length"
                        :key="pos"
                        flat
                        :label="pos"
                        :text-color="
                        getEntry(member.id).starting_position === pos
                          ? 'secondary'
                          : 'grey-7'
                      "
                        dense
                        :disable="isPosLockedFor(member.id, pos)"
                        @click="setStartingPosition(member.id, pos)"
                      />
                    </q-btn-group>
                  </div>
                </div>

                <KennerSelect
                  v-if="resultConfig?.is_asymmetric"
                  v-model="getEntry(member.id).faction_id"
                  :options="factions"
                  option-label="name"
                  option-value="id"
                  label="Faction"
                  dense
                  outlined
                />

                <q-input
                  v-if="tieBreakerRequired"
                  v-model="getEntry(member.id).tie_breaker_value"
                  label="Tie-Breaker Wert"
                  dense
                  outlined
                />
              </q-card-section>
            </q-card>
          </div>
        </div>

        <div class="row justify-end">
          <q-btn
            type="submit"
            label="Save Result"
            color="primary"
            unelevated
          />
        </div>
      </q-form>

      <q-spinner v-else color="primary" size="md" class="q-my-xl" />
    </div>
  </q-card>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { api } from 'boot/axios';
import { useQuasar } from 'quasar';
import { storeToRefs } from 'pinia';
import { useLeagueStore } from 'stores/leagueStore';
import KennerInput from 'components/base/KennerInput.vue';
import KennerSelect from 'components/base/KennerSelect.vue';

const emit = defineEmits<{ (e: 'submitted', selectedGameId: number): void }>();
const $q = useQuasar();

const props = defineProps<{ selectedGameId: number }>();
const { members } = storeToRefs(useLeagueStore());

const resultConfig = ref<any>(null);
const factions = ref<Array<{ id: number; name: string }>>([]);
const formData = ref<Array<any>>([]);
const tieBreakerRequired = ref(false);
const orderByStartingPos = ref(true); // toggle for display order

// Helpers to access entries by member id (stable even if we reorder display)
function getEntry(memberId: number) {
  let found = formData.value.find((e) => e.player_profile === memberId);
  // Defensive (shouldn't happen)
  if (!found) {
    found = {
      player_profile: memberId,
      selected_game: props.selectedGameId,
      points: null,
      starting_position: null,
      faction_id: null,
      tie_breaker_value: '',
    };
    formData.value.push(found);
  }
  return found;
}

// Preselect 1..n, unique
function preselectStartingPositions() {
  const n = members.value.length;
  members.value.forEach((m, i) => {
    getEntry(m.id).starting_position = i + 1; // 1..n
  });
}

// Called when user sets a position for a member
function setStartingPosition(memberId: number, newPos: number) {
  const n = members.value.length;
  // 1) Lock in left side order: we consider the natural "members" order left->right.
  const indexOf = (id: number) => members.value.findIndex((m) => m.id === id);
  const i = indexOf(memberId);

  // 2) Assign chosen pos to this player
  getEntry(memberId).starting_position = newPos;

  // 3) Build a set of taken positions from players on the left INCLUDING current
  const taken = new Set<number>();
  for (let k = 0; k <= i; k++) {
    const pos = getEntry(members.value[k].id).starting_position;
    if (pos) taken.add(pos);
  }

  // 4) Repack right side with next available positions ascending
  let next = 1;
  const nextFree = () => {
    while (taken.has(next) && next <= n) next++;
    return next <= n ? next : null;
  };

  for (let k = i + 1; k < n; k++) {
    const entry = getEntry(members.value[k].id);
    // If current choice conflicts or is empty, assign the next free
    if (!entry.starting_position || taken.has(entry.starting_position)) {
      const nf = nextFree();
      if (nf !== null) {
        entry.starting_position = nf;
        taken.add(nf);
      }
    } else {
      // Keep current if unique; also mark as taken
      taken.add(entry.starting_position);
    }
  }
}

// Disable positions already locked by players to the left (visual hint)
function isPosLockedFor(memberId: number, pos: number) {
  const idx = members.value.findIndex((m) => m.id === memberId);
  for (let k = 0; k < idx; k++) {
    if (getEntry(members.value[k].id).starting_position === pos) return true;
  }
  return false;
}

// Display order (optional): by starting_position then by original member order
const displayMembers = computed(() => {
  if (!orderByStartingPos.value) return members.value;

  const byStart = [...members.value].sort((a, b) => {
    const pa = getEntry(a.id).starting_position ?? Infinity;
    const pb = getEntry(b.id).starting_position ?? Infinity;
    if (pa !== pb) return pa - pb;
    // stable tie: keep original index
    return (
      members.value.findIndex((m) => m.id === a.id) -
      members.value.findIndex((m) => m.id === b.id)
    );
  });
  return byStart;
});

async function fetchResultConfig() {
  const { data: selectedGame } = await api.get(
    `game/selected-games/${props.selectedGameId}/`
  );
  const gameId = selectedGame.game;
  if (!gameId) {
    console.warn('Game ID not found');
    return;
  }
  const { data } = await api.get(`game/result-configs/?game=${gameId}`);
  resultConfig.value = data[0];
}

async function fetchFactions() {
  const { data } = await api.get(
    `game/selected-games/${props.selectedGameId}/`
  );
  const gameId = data.game;
  const factionRes = await api.get(`game/factions/?game=${gameId}`);
  factions.value = factionRes.data;
}

function initFormData() {
  formData.value = members.value.map((p) => ({
    player_profile: p.id,
    selected_game: props.selectedGameId,
    points: null,
    starting_position: null,
    faction_id: null,
    tie_breaker_value: '',
  }));
  tieBreakerRequired.value = false;
  preselectStartingPositions();
}

watch(
  () => props.selectedGameId,
  async () => {
    if (props.selectedGameId) {
      await fetchResultConfig();
      await fetchFactions();
      initFormData();
    }
  },
  { immediate: true }
);

async function submitResults() {
  // Sanitize faction_id fields
  formData.value = formData.value.map((entry) => ({
    ...entry,
    faction_id:
      entry.faction_id !== null &&
      typeof entry.faction_id === 'object' &&
      'id' in entry.faction_id
        ? entry.faction_id.id
        : entry.faction_id ?? null,
  }));

  const payload = {
    selected_game: props.selectedGameId,
    results: formData.value,
  };

  try {
    const response = await api.post('/result/match-results/', payload);
    if (response.status === 201) {
      $q.notify({ type: 'positive', message: 'Match gespeichert.' });
      emit('submitted', props.selectedGameId);
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
        message: 'Error saving match results.',
      });
    }
  }
}
</script>

<style scoped>
.form-card-header {
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}
</style>

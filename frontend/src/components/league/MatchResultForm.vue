<template>
  <q-card class="q-pa-md" flat bordered rounded>
    <div class="row items-center q-mb-sm">
      <div class="col">
        <div class="text-h6 text-primary">Match Result</div>
        <div class="text-caption text-grey-7">{{ members.length }} players</div>
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

    <div class="q-pa-sm">
      <q-form v-if="formData.length" @submit.prevent="submitResults">
        <div class="row q-col-gutter-sm q-mb-xl">
          <div
            v-for="member in displayMembers"
            :key="member.id"
            class="col-12 col-sm-6 col-md-4 col-lg-3"
          >
            <q-card flat bordered class="member-card">
              <q-card-section class="row items-center justify-between q-py-xs q-px-sm">
                <div class="text-subtitle2 ellipsis">{{ member.username }}</div>
                <q-chip
                  v-if="getEntry(member.id).starting_position"
                  dense outline square size="sm"
                >
                  #{{ getEntry(member.id).starting_position }}
                </q-chip>
              </q-card-section>

              <q-separator spaced inset />

              <q-card-section class="q-gutter-xs q-pt-sm q-pb-sm">
                <!-- Points -->
                <KennerInput
                  v-if="resultConfig?.has_points"
                  v-model.number="getEntry(member.id).points"
                  type="number"
                  inputmode="numeric"
                  label="Points"
                  dense
                  outlined
                  hide-bottom-space
                  :suffix="'pts'"
                  :rules="[(v:string|number|null) => v !== null && v !== '' || 'Points required']"
                >
                  <template #prepend>
                    <q-icon name="score" size="16px" class="q-mr-xs" />
                  </template>
                </KennerInput>

                <!-- Starting position -->
                <div class="row items-center no-wrap justify-between">
                  <div>
                    <q-badge color="grey-8" text-color="grey-2" class="q-mr-xs" outline>Start</q-badge>
                    <span class="text-caption text-grey-7">Position</span>
                  </div>
                  <div class="row items-center q-gutter-xs">
                    <div
                      v-for="pos in members.length"
                      :key="pos"
                      class="col-auto"
                    >
                      <q-btn

                        size="sm"
                        no-caps
                        outline
                        :color="getEntry(member.id).starting_position === pos ? 'white' : 'grey-6'"
                        :class="[{'bg-secondary' : getEntry(member.id).starting_position === pos}]"
                        :label="pos"
                        @click="swapStartingPosition(member.id, pos)"
                      />
                    </div>
                  </div>
                </div>

                <div class="row items-center q-col-gutter-xs q-mt-xs justify-center">
                </div>

                <!-- Faction -->
                <KennerSelect
                  v-if="resultConfig?.is_asymmetric"
                  v-model="getEntry(member.id).faction_id"
                  :options="factions"
                  option-label="name"
                  option-value="id"
                  label="Faction"
                  dense
                  outlined
                  hide-bottom-space
                  clearable
                  options-dense
                >
                  <template #prepend>
                    <q-icon name="groups" size="16px" class="q-mr-xs" />
                  </template>
                </KennerSelect>

                <!-- Tie-Breaker -->
                <q-input
                  v-if="tieBreakerRequired"
                  v-model="getEntry(member.id).tie_breaker_value"
                  label="Tie-breaker"
                  dense
                  outlined
                  hide-bottom-space
                >
                  <template #prepend>
                    <q-icon name="toll" size="16px" class="q-mr-xs" />
                  </template>
                </q-input>
              </q-card-section>
            </q-card>
          </div>
        </div>

        <div class="row justify-end q-gutter-sm q-pt-xs q-pb-sm bg-white">
          <q-btn flat color="secondary" icon="refresh" label="Reset" @click="initFormData" />
          <q-btn type="submit" label="Save Result" color="primary" unelevated />
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
const orderByStartingPos = ref(true);

// ---- helpers (unchanged) ----
function getEntry(memberId: number) {
  let found = formData.value.find((e) => e.player_profile === memberId);
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

function preselectStartingPositions() {
  members.value.forEach((m, i) => {
    getEntry(m.id).starting_position = i + 1;
  });
}

/**
 * NEW: swap behavior (no locks, no disables)
 * If target position is taken, swap with its owner; otherwise just assign.
 */
function swapStartingPosition(memberId: number, newPos: number) {
  const currentPos = getEntry(memberId).starting_position ?? null;
  if (currentPos === newPos) return;

  // find owner of newPos (if any)
  const owner = members.value.find(
    (m) => getEntry(m.id).starting_position === newPos
  );

  // assign new position to clicked member
  getEntry(memberId).starting_position = newPos;

  // if someone owned that position, give them the old one (can become null)
  if (owner && owner.id !== memberId) {
    getEntry(owner.id).starting_position = currentPos;
  }
}

// removed: isPosLockedFor + left-to-right packing

const displayMembers = computed(() => {
  if (!orderByStartingPos.value) return members.value;

  const byStart = [...members.value].sort((a, b) => {
    const pa = getEntry(a.id).starting_position ?? Infinity;
    const pb = getEntry(b.id).starting_position ?? Infinity;
    if (pa !== pb) return pa - pb;
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
  if (!gameId) return;
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

// submitResults unchanged...
async function submitResults() {
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
      $q.notify({ type: 'positive', message: 'Result saved.' });
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
.member-card { border-radius: 10px; background: #fff; }
.ellipsis { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>

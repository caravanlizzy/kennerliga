<template>
  <q-card class="q-pa-md" flat bordered rounded>
    <div class="row items-center q-mb-md">
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

    <!-- Tie-breaker banner -->
    <q-banner
      v-if="tieBreakerRequired && requiredTieBreaker"
      class="q-mb-md bg-warning text-dark"
      rounded
      dense
    >
      <template #avatar>
        <q-icon name="toll" />
      </template>
      <div class="text-body2">
        <b>{{ requiredTieBreaker.name }}</b> needed for:
        <span v-for="(grp, idx) in tieGroupDisplay" :key="grp.key">
          {{ grp.names.join(', ')
          }}<span v-if="idx < tieGroupDisplay.length - 1">; </span>
        </span>
      </div>
    </q-banner>

    <div class="q-pa-sm">
      <q-form v-if="formData.length" @submit.prevent="submitResults">
        <div class="row q-col-gutter-md q-mb-md">
          <div
            v-for="member in displayMembers"
            :key="member.id"
            class="col-12 col-sm-6 col-lg-3"
          >
            <q-card flat bordered class="member-card">
              <q-card-section class="q-pa-sm">
                <div class="row items-center justify-between q-mb-sm">
                  <div class="text-subtitle2 text-weight-medium ellipsis">
                    {{ member.username }}
                  </div>
                </div>

                <div class="column q-gutter-sm">
                  <!-- Points -->
                  <q-input
                    v-if="resultConfig?.has_points"
                    v-model.number="getEntry(member.id).points"
                    type="number"
                    inputmode="numeric"
                    label="Points"
                    dense
                    outlined
                    hide-bottom-space
                    class="points-input"
                    bg-color="grey-2"
                    :rules="[(v:string|number|null) => v !== null && v !== '' || 'Required']"
                  />

                  <!-- Faction -->
                  <KennerSelect
                    v-if="resultConfig?.is_asymmetric"
                    v-model="getEntry(member.id).faction_id"
                    :options="factions"
                    option-label="name"
                    option-value="id"
                    emit-value
                    map-options
                    label="Faction"
                    dense
                    outlined
                    hide-bottom-space
                    clearable
                    options-dense
                  />

                  <!-- Starting position -->
                  <div>
                    <div class="text-caption text-grey-7 q-mb-xs">
                      Starting Position
                    </div>
                    <div class="row q-gutter-sm justify-center">
                      <q-btn
                        v-for="pos in members.length"
                        :key="pos"
                        size="md"
                        round
                        :outline="getEntry(member.id).starting_position !== pos"
                        :unelevated="
                          getEntry(member.id).starting_position === pos
                        "
                        :color="
                          getEntry(member.id).starting_position === pos
                            ? 'secondary'
                            : 'grey-4'
                        "
                        :text-color="
                          getEntry(member.id).starting_position === pos
                            ? 'white'
                            : 'grey-8'
                        "
                        :label="String(pos)"
                        class="position-btn"
                        @click="swapStartingPosition(member.id, pos)"
                      />
                    </div>
                  </div>

                  <!-- Tie-Breaker -->
                  <q-input
                    v-if="tieBreakerRequired && needsTieBreaker(member.id)"
                    v-model.number="getEntry(member.id).tie_breaker_value"
                    :label="requiredTieBreaker?.name || 'Tie-breaker'"
                    type="number"
                    inputmode="decimal"
                    dense
                    outlined
                    hide-bottom-space
                  />
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>

        <div class="row justify-end q-gutter-sm">
          <q-btn flat color="secondary" label="Reset" @click="initFormData" />
          <q-btn
            type="submit"
            :label="submitLabel"
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

type Faction = { id: number; name: string };
type Member = { id: number; username: string };

const emit = defineEmits<{ (e: 'submitted', selectedGameId: number): void }>();
const $q = useQuasar();

const props = defineProps<{ selectedGameId: number; leagueId: number }>();
const leagueStore = useLeagueStore(props.leagueId)();
const { members } = storeToRefs(leagueStore); // Member[]

const resultConfig = ref<any>(null);
const factions = ref<Faction[]>([]);
const formData = ref<any[]>([]);

// tie-breaker UI state
const tieBreakerRequired = ref(false);
const requiredTieBreaker = ref<{
  id: number;
  name?: string;
  order?: number;
} | null>(null);
const tieBreakerPlayers = ref<Set<number>>(new Set()); // ids needing value now
const tieGroups = ref<Array<{ points: number; players: number[] }>>([]); // for banner

const orderByStartingPos = ref(true);

const tieBreakerLabel = computed(() =>
  requiredTieBreaker.value?.name
    ? `Tie-breaker: ${requiredTieBreaker.value.name}`
    : 'Tie-breaker'
);
const submitLabel = computed(() =>
  tieBreakerRequired.value ? 'Submit Tie-Breakers' : 'Save Result'
);

function getEntry(memberId: number) {
  let found = formData.value.find((e) => e.player_profile === memberId);
  if (!found) {
    found = {
      player_profile: memberId,
      selected_game: props.selectedGameId,
      points: null as number | null,
      starting_position: null as number | null,
      faction_id: null as number | null, // ID (emit-value + map-options)
      tie_breaker_value: null as number | null,
    };
    formData.value.push(found);
  }
  return found;
}

function preselectStartingPositions() {
  (members.value as Member[]).forEach((m, i) => {
    getEntry(m.id).starting_position = i + 1;
  });
}

/** Swap start positions */
function swapStartingPosition(memberId: number, newPos: number) {
  const currentPos = getEntry(memberId).starting_position ?? null;
  if (currentPos === newPos) return;

  const owner = (members.value as Member[]).find(
    (m) => getEntry(m.id).starting_position === newPos
  );
  getEntry(memberId).starting_position = newPos;
  if (owner && owner.id !== memberId) {
    getEntry(owner.id).starting_position = currentPos;
  }
}

const displayMembers = computed(() => {
  if (!orderByStartingPos.value) return members.value as Member[];
  const byStart = [...(members.value as Member[])].sort((a, b) => {
    const pa = getEntry(a.id).starting_position ?? Infinity;
    const pb = getEntry(b.id).starting_position ?? Infinity;
    if (pa !== pb) return pa - pb;
    return (
      (members.value as Member[]).findIndex((m) => m.id === a.id) -
      (members.value as Member[]).findIndex((m) => m.id === b.id)
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
  resultConfig.value = data?.[0] ?? null;
}

async function fetchFactions() {
  const { data } = await api.get(
    `game/selected-games/${props.selectedGameId}/`
  );
  const gameId = data.game;
  const factionRes = await api.get(`game/factions/?game=${gameId}`);
  factions.value = (factionRes.data ?? []) as Faction[];
}

function initFormData() {
  formData.value = (members.value as Member[]).map((p) => ({
    player_profile: p.id,
    selected_game: props.selectedGameId,
    points: null as number | null,
    starting_position: null as number | null,
    faction_id: null as number | null,
    tie_breaker_value: null as number | null,
  }));
  preselectStartingPositions();

  // reset tie-breaker UI
  tieBreakerRequired.value = false;
  requiredTieBreaker.value = null;
  tieBreakerPlayers.value = new Set();
  tieGroups.value = [];
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

function idToName(pid: number) {
  const m = (members.value as Member[]).find((x) => x.id === pid);
  return m?.username ?? `#${pid}`;
}

const tieGroupDisplay = computed(() =>
  tieGroups.value.map((g) => ({
    key: `${g.points}-${g.players.join('-')}`,
    points: g.points,
    names: g.players.map(idToName),
  }))
);

function needsTieBreaker(memberId: number) {
  return tieBreakerRequired.value && tieBreakerPlayers.value.has(memberId);
}

/** Parse backend 202 payload and update UI */
function handleTieBreaker202(data: any) {
  tieBreakerRequired.value = true;
  requiredTieBreaker.value = data?.required_tie_breaker ?? null;

  const nextPlayers = new Set<number>();
  if (Array.isArray(data?.tie_groups)) {
    tieGroups.value = data.tie_groups as Array<{
      points: number;
      players: number[];
    }>;
    for (const g of data.tie_groups) {
      for (const pid of g.players ?? []) nextPlayers.add(pid);
    }
  } else {
    tieGroups.value = [];
  }

  // fallback legacy key
  if (!data?.tie_groups && Array.isArray(data?.tied_players)) {
    for (const pid of data.tied_players) nextPlayers.add(pid);
  }

  tieBreakerPlayers.value = nextPlayers;

  const tbName = requiredTieBreaker.value?.name
    ? ` (${requiredTieBreaker.value.name})`
    : '';
  const list = [...nextPlayers].map(idToName).join(', ') || 'unknown';
  $q.notify({
    type: 'warning',
    message: `Tie detected${tbName}. Please enter tie-breaker values for: ${list}.`,
  });
}

async function submitResults() {
  // If in tie-breaker step, ensure all required players provided a value
  if (tieBreakerRequired.value) {
    const missing = [...tieBreakerPlayers.value].filter((pid) => {
      const v = getEntry(pid).tie_breaker_value;
      return v === null || v === '' || Number.isNaN(Number(v));
    });
    if (missing.length) {
      $q.notify({
        type: 'negative',
        message: `Please enter a tie-breaker value for: ${missing
          .map(idToName)
          .join(', ')}`,
      });
      return;
    }
  }

  const results = formData.value.map((entry) => ({
    player_profile: entry.player_profile,
    selected_game: entry.selected_game,
    points: entry.points,
    starting_position: entry.starting_position,
    faction_id: entry.faction_id ?? null,
    tie_breaker_value: entry.tie_breaker_value ?? null,
  }));

  const payload: any = {
    selected_game: props.selectedGameId,
    results,
  };

  if (tieBreakerRequired.value && requiredTieBreaker.value?.id) {
    payload.tiebreaker = { id: requiredTieBreaker.value.id };
  }

  try {
    const response = await api.post('/result/match-results/', payload);

    if (response.status === 201) {
      $q.notify({ type: 'positive', message: 'Result saved.' });
      emit('submitted', props.selectedGameId);
      // reset tie UI
      tieBreakerRequired.value = false;
      requiredTieBreaker.value = null;
      tieBreakerPlayers.value = new Set();
      tieGroups.value = [];
      return;
    }

    if (response.status === 202) {
      handleTieBreaker202(response.data);
      return;
    }

    // Any unexpected success code
    $q.notify({
      type: 'warning',
      message: `Unexpected status ${response.status}.`,
    });
  } catch (err: any) {
    const data = err?.response?.data;
    if (data?.detail) {
      $q.notify({ type: 'negative', message: data.detail });
    } else {
      console.error('Error submitting results:', err);
      $q.notify({ type: 'negative', message: 'Error saving match results.' });
    }
  }
}
</script>

<style scoped>
.member-card {
  border-radius: 10px;
  background: #fff;
}
.ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.position-btn {
  min-width: 40px;
  min-height: 40px;
  font-weight: 500;
  font-size: 15px;
}
</style>

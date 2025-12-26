<template>
  <q-card class="q-pa-md" flat bordered rounded>
    <div class="row items-center q-mb-md">
      <div class="col">
        <div class="text-h6 text-dark">Match Result</div>
        <div class="text-caption text-grey-7">{{ members.length }} players</div>
      </div>
    </div>

    <!-- Tie-breaker banner -->
    <q-banner
      v-if="tieBreakerRequired"
      class="q-mb-md bg-warning text-dark"
      rounded
      dense
    >
      <template #avatar>
        <q-icon name="toll" />
      </template>
      <div class="text-body2">
        <template v-if="requiredTieBreaker?.name">
          <b>{{ requiredTieBreaker.name }}</b> needed for:
        </template>
        <template v-else> <b>Tie-breaker</b> needed for: </template>
        <span v-for="(grp, idx) in tieGroupDisplay" :key="grp.key">
          {{ grp.names.join(', ')
          }}<span v-if="idx < tieGroupDisplay.length - 1">; </span>
        </span>
      </div>
    </q-banner>

    <div class="q-pa-sm">
      <q-form
        v-if="!isLoading && formData.length"
        @submit.prevent="submitResults"
      >
        <div class="row q-col-gutter-md q-mb-md">
          <div
            v-for="member in members"
            :key="member.id"
            class="col-12 col-sm-6 col-lg-3"
          >
            <q-card flat bordered class="member-card">
              <q-card-section class="q-pa-sm">
                <div class="row items-center justify-between q-mb-sm">
                  <div class="text-subtitle2 text-weight-medium ellipsis">
                    {{ member.profile_name }}
                  </div>
                </div>

                <div class="column q-gutter-sm">
                  <!-- Points (for points-based games) -->
                  <q-input
                    v-if="resultConfig?.has_points"
                    v-model.number="getEntry(member.profile).points"
                    type="number"
                    inputmode="numeric"
                    label="Points"
                    dense
                    outlined
                    hide-bottom-space
                    class="points-input"
                    bg-color="grey-2"
                    :rules="[(v:any) => v !== null && v !== '' || 'Required']"
                  />

                  <!-- Position (for non-points games) -->
                  <div v-else>
                    <div class="text-caption text-grey-7 q-mb-xs">
                      Final Position
                    </div>
                    <div class="row q-gutter-sm justify-center">
                      <q-btn
                        v-for="pos in members.length"
                        :key="pos"
                        size="md"
                        round
                        :outline="getEntry(member.profile).position !== pos"
                        :unelevated="getEntry(member.profile).position === pos"
                        :color="
                          getEntry(member.profile).position === pos
                            ? 'dark'
                            : 'grey-4'
                        "
                        :text-color="
                          getEntry(member.profile).position === pos
                            ? 'white'
                            : 'grey-8'
                        "
                        :label="String(pos)"
                        class="position-btn"
                        @click="setPosition(member.id, pos)"
                      />
                    </div>
                    <!-- Notes for position -->
                    <q-input
                      v-model="getEntry(member.profile).notes"
                      label="Position Note"
                      placeholder="Explain position reason..."
                      dense
                      outlined
                      hide-bottom-space
                      class="q-mt-sm"
                      type="textarea"
                      autogrow
                      :input-style="{ minHeight: '40px' }"
                    />
                  </div>

                  <!-- Factions by Level -->
                  <div v-if="resultConfig?.is_asymmetric">
                    <KennerSelect
                      v-for="level in sortedFactionLevels"
                      :key="level"
                      v-model="getEntry(member.profile).faction_ids[level]"
                      :options="factionsByLevel[level]"
                      option-label="name"
                      option-value="id"
                      emit-value
                      map-options
                      :label="
                        level === 0 ? 'Faction' : `Level ${level} Faction`
                      "
                      dense
                      outlined
                      hide-bottom-space
                      clearable
                      options-dense
                      class="q-mb-xs"
                    />
                  </div>

                  <!-- Starting position -->
                  <div>
                    <div
                      class="text-caption text-grey-7 q-mb-xs"
                      style="font-size: 11px"
                    >
                      Starting Position
                    </div>
                    <div class="row q-gutter-xs justify-center">
                      <q-btn
                        v-for="pos in members.length"
                        :key="pos"
                        size="sm"
                        round
                        :outline="
                          getEntry(member.profile).starting_position !== pos
                        "
                        :unelevated="
                          getEntry(member.profile).starting_position === pos
                        "
                        :color="
                          getEntry(member.profile).starting_position === pos
                            ? 'secondary'
                            : 'grey-5'
                        "
                        :text-color="
                          getEntry(member.profile).starting_position === pos
                            ? 'white'
                            : 'grey-7'
                        "
                        :label="String(pos)"
                        class="starting-position-btn"
                        @click="swapStartingPosition(member.id, pos)"
                      />
                    </div>
                  </div>

                  <!-- Starting Points -->
                  <q-input
                    v-if="
                      resultConfig?.starting_points_system &&
                      resultConfig.starting_points_system === 'FIX'
                    "
                    v-model.number="getEntry(member.profile).starting_points"
                    type="number"
                    inputmode="numeric"
                    label="Starting Points"
                    dense
                    outlined
                    hide-bottom-space
                    class="q-mt-xs"
                    bg-color="blue-1"
                    :rules="[
                      (v:any) => (v !== null && v !== '') || 'Required'
                    ]"
                  />

                  <!-- Tie-Breaker (Appears only when a tie needs resolving) -->
                  <div
                    v-if="tieBreakerRequired && needsTieBreaker(member.profile)"
                    class="q-mt-sm"
                  >
                    <q-input
                      v-model.number="
                        getEntry(member.profile).tie_breaker_value
                      "
                      :label="requiredTieBreaker?.name || 'Tie-breaker Value'"
                      type="number"
                      inputmode="decimal"
                      dense
                      outlined
                      color="orange-8"
                      bg-color="orange-1"
                      hide-bottom-space
                      :rules="[(v:any) => v !== null && v !== '' || 'Tie-breaker value required']"
                    >
                      <template #prepend>
                        <q-icon name="balance" size="xs" color="orange-9" />
                      </template>
                    </q-input>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>

        <div class="row justify-end q-gutter-sm">
          <q-btn
            rounded
            flat
            color="secondary"
            label="Reset"
            @click="initFormData"
          />
          <KennerButton
            type="submit"
            :label="submitLabel"
            color="dark"
            unelevated
          />
        </div>
      </q-form>

      <q-spinner v-else color="dark" size="md" class="q-my-xl" />
    </div>
  </q-card>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { api } from 'boot/axios';
import { useQuasar } from 'quasar';
import { storeToRefs } from 'pinia';
import { useLeagueStore } from 'stores/leagueStore';
import KennerSelect from 'components/base/KennerSelect.vue';
import KennerButton from 'components/base/KennerButton.vue';

type Faction = { id: number; name: string; level: number };

const emit = defineEmits<{ (e: 'submitted', selectedGameId: number): void }>();
const $q = useQuasar();

const props = defineProps<{ selectedGameId: number; leagueId: number }>();
const leagueStore = useLeagueStore(props.leagueId)();
const { members } = storeToRefs(leagueStore);

const resultConfig = ref<any>(null);
const factions = ref<Faction[]>([]);
const formData = ref<any[]>([]);
const isLoading = ref(false);

const tieBreakerRequired = ref(false);
const requiredTieBreaker = ref<{
  id: number;
  name?: string;
  order?: number;
} | null>(null);
const tieBreakerPlayers = ref<Set<number>>(new Set());
const tieGroups = ref<
  Array<{ points: number | null; position: number | null; players: number[] }>
>([]);

const submitLabel = computed(() =>
  tieBreakerRequired.value ? 'Submit Tie-Breakers' : 'Save Result'
);

const factionsByLevel = computed(() => {
  const groups: Record<number, Faction[]> = {};
  factions.value.forEach((f) => {
    const lvl = f.level ?? 0;
    if (!groups[lvl]) groups[lvl] = [];
    groups[lvl].push(f);
  });
  return groups;
});

const sortedFactionLevels = computed(() =>
  Object.keys(factionsByLevel.value)
    .map(Number)
    .sort((a, b) => a - b)
);

function getEntry(profileId: number) {
  let found = formData.value.find((e) => e.player_profile === profileId);
  if (!found) {
    found = {
      player_profile: profileId,
      selected_game: props.selectedGameId,
      points: null as number | null,
      position: null as number | null,
      notes: '' as string,
      starting_position: null as number | null,
      starting_points: null as number | null,
      faction_ids: {} as Record<number, number | null>,
      tie_breaker_value: null as number | null,
    };
    formData.value.push(found);
  }
  return found;
}

function preselectStartingPositions() {
  members.value.forEach((m, i) => {
    getEntry(m.profile).starting_position = i + 1;
  });
}

function swapStartingPosition(memberId: number, newPos: number) {
  const member = members.value.find((m) => m.id === memberId);
  if (!member) return;
  const currentPos = getEntry(member.profile).starting_position ?? null;
  if (currentPos === newPos) return;

  const owner = members.value.find(
    (m) => getEntry(m.profile).starting_position === newPos
  );
  getEntry(member.profile).starting_position = newPos;
  if (owner && owner.profile !== member.profile) {
    getEntry(owner.profile).starting_position = currentPos;
  }
}

function setPosition(memberId: number, pos: number) {
  const member = members.value.find((m) => m.id === memberId);
  if (!member) return;
  const entry = getEntry(member.profile);
  if (entry.position === pos) {
    entry.position = null;
  } else {
    entry.position = pos;
  }
}

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
  if (!members.value || members.value.length === 0) {
    formData.value = [];
    return;
  }

  formData.value = members.value.map((p) => ({
    player_profile: p.profile,
    selected_game: props.selectedGameId,
    points: null as number | null,
    position: null as number | null,
    notes: '' as string,
    starting_position: null as number | null,
    starting_points: null as number | null,
    faction_ids: {} as Record<number, number | null>,
    tie_breaker_value: null as number | null,
  }));
  preselectStartingPositions();

  tieBreakerRequired.value = false;
  requiredTieBreaker.value = null;
  tieBreakerPlayers.value = new Set();
  tieGroups.value = [];
}

watch(
  () => props.selectedGameId,
  async () => {
    if (props.selectedGameId) {
      isLoading.value = true;
      try {
        await Promise.all([fetchResultConfig(), fetchFactions()]);
        initFormData();
      } catch (error) {
        console.error('Error loading form data:', error);
      } finally {
        isLoading.value = false;
      }
    }
  },
  { immediate: true }
);

watch(
  () => members.value,
  (newMembers) => {
    if (
      newMembers &&
      newMembers.length > 0 &&
      formData.value.length === 0 &&
      !isLoading.value
    ) {
      initFormData();
    }
  },
  { immediate: true }
);

function idToName(profileId: number) {
  const m = members.value.find((x) => x.profile === profileId);
  return m?.profile_name;
}

const tieGroupDisplay = computed(() =>
  tieGroups.value.map((g, index) => ({
    key: `${index}-${g.players.join('-')}`,
    points: g.points,
    names: g.players.map(idToName),
  }))
);

function needsTieBreaker(profileId: number) {
  return tieBreakerRequired.value && tieBreakerPlayers.value.has(profileId);
}

function handleTieBreaker202(data: any) {
  tieBreakerRequired.value = true;
  requiredTieBreaker.value = data?.required_tie_breaker ?? null;

  const nextPlayers = new Set<number>();
  if (Array.isArray(data?.tie_groups)) {
    tieGroups.value = data.tie_groups;
    for (const g of data.tie_groups) {
      for (const pid of g.players ?? []) nextPlayers.add(pid);
    }
  } else {
    tieGroups.value = [];
  }

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

  const results = formData.value.map((entry) => {
    const selectedFactionIds = Object.values(entry.faction_ids || []).filter(
      (id) => id !== null && id !== undefined
    ) as number[];

    return {
      player_profile: entry.player_profile,
      selected_game: entry.selected_game,
      points: resultConfig.value?.has_points ? entry.points : null,
      position: !resultConfig.value?.has_points ? entry.position : null,
      notes: entry.notes || null,
      starting_position: entry.starting_position,
      starting_points: entry.starting_points,
      faction_ids: selectedFactionIds,
      tie_breaker_value: entry.tie_breaker_value ?? null,
    };
  });

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
      tieBreakerRequired.value = false;
      return;
    }

    if (response.status === 202) {
      handleTieBreaker202(response.data);
      return;
    }
  } catch (err: any) {
    const data = err?.response?.data;
    $q.notify({
      type: 'negative',
      message: data?.detail || 'Error saving results.',
    });
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

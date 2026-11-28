<template>
  <q-card class="q-pa-lg" flat bordered rounded>
    <div class="row items-center q-mb-lg q-col-gutter-md">
      <div class="col-12 col-md">
        <div class="text-h5 text-weight-bold text-dark">
          <q-icon name="emoji_events" color="primary" class="q-mr-sm" />
          Match Result
        </div>
        <div class="text-subtitle2 text-grey-6">
          {{ members.length }} Players Participating
        </div>
      </div>

      <!-- Win Condition selector -->
      <div v-if="winConditions.length > 0" class="col-12 col-md-auto">
        <q-card flat bordered class="q-pa-sm wc-card">
          <div class="row items-center q-gutter-x-md">
            <div class="text-subtitle2 text-weight-bold q-ml-sm">
              <q-icon name="flag_circle" color="primary" class="q-mr-xs" />
              Win Condition
            </div>
            <q-option-group
              v-model="selectedWinConditionId"
              :options="
                winConditions.map((wc) => ({ label: wc.name, value: wc.id }))
              "
              color="primary"
              type="radio"
              inline
              dense
            />
          </div>
        </q-card>
      </div>
    </div>

    <!-- Tie-breaker banner -->
    <TieBreakerBanner
      :tie-breaker-required="tieBreakerRequired"
      :required-tie-breaker="requiredTieBreaker"
      :tie-group-display="tieGroupDisplay"
    />

    <div class="q-pa-sm">
      <q-form
        v-if="!isLoading && formData.length"
        @submit.prevent="submitResults"
      >
        <div class="row q-mb-md">
          <q-input
            v-model="gameLink"
            class="col-12"
            outlined
            dense
            type="url"
            label="Game link"
            hint="Optional link to the game session or recording."
            :rules="[validateGameLink]"
          >
            <template #prepend>
              <q-icon name="link" />
            </template>
          </q-input>
        </div>

        <div class="row q-col-gutter-md q-mb-md">
          <div
            v-for="member in members"
            :key="member.id"
            class="col-12 col-sm-6"
          >
            <GameResultFields
              :member="member"
              :entry="getEntry(member.profile)"
              :members-count="members.length"
              :win-condition-is-points="winConditionIsPoints"
              :win-condition-is-option="winConditionIsOption"
              :selected-win-condition="selectedWinCondition"
              :result-config="resultConfig"
              :sorted-faction-levels="sortedFactionLevels"
              :factions-by-level="factionsByLevel"
              :tie-breaker-required="tieBreakerRequired"
              :needs-tie-breaker="needsTieBreaker(member.profile)"
              :required-tie-breaker="requiredTieBreaker"
              @set-position="setPosition"
              @swap-starting-position="swapStartingPosition"
            />
          </div>
        </div>

        <div class="row justify-end q-gutter-md q-mt-lg">
          <KennerButton
            rounded
            unelevated
            color="grey-4"
            text-color="grey-9"
            label="Reset Form"
            class="q-px-md"
            @click="initFormData"
          />
          <KennerButton
            type="submit"
            :label="submitLabel"
            color="primary"
            unelevated
            rounded
            class="q-px-xl text-weight-bold"
          />
        </div>
      </q-form>

      <LoadingSpinner v-else />
    </div>
  </q-card>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import {
  fetchMatchResults,
  fetchOrderedWinConditions,
  fetchSelectedGame,
  submitMatchResults,
} from 'src/services/resultService';
import {
  fetchFactionsForGame,
  fetchResultConfigForGame,
} from 'src/services/gameService';
import { useQuasar } from 'quasar';
import { storeToRefs } from 'pinia';
import { useLeagueStore } from 'stores/leagueStore';
import KennerButton from 'components/base/KennerButton.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import TieBreakerBanner from 'components/league/TieBreakerBanner.vue';
import GameResultFields from 'components/league/GameResultFields.vue';
import {
  TLeagueDto,
  TResultConfigDto,
  TTieBreakerDto,
  TMatchResultPayload,
  TMatchResultSubmitPayload,
  TWinConditionDto,
} from 'src/types';

type Faction = { id: number; name: string; level: number };

type FormDataEntry = {
  player_profile: number;
  selected_game: number;
  points: number | null;
  position: number | null;
  notes: string;
  starting_position: number | null;
  starting_points: number | null;
  faction_ids: Record<number, number | null>;
  tie_breaker_value: number | null;
  win_condition_option: number | null;
};

const emit = defineEmits<{ (e: 'submitted', selectedGameId: number): void }>();
const $q = useQuasar();

const props = defineProps<{
  selectedGameId: number;
  leagueId: number;
  league?: TLeagueDto;
}>();
const leagueStore = useLeagueStore(props.leagueId)();
const { members, initialized } = storeToRefs(leagueStore);

onMounted(() => {
  if (!initialized.value) {
    leagueStore.init();
  }
});

const resultConfig = ref<TResultConfigDto | null>(null);
const factions = ref<Faction[]>([]);
const formData = ref<FormDataEntry[]>([]);
const gameLink = ref('');
const initialGameLink = ref('');
const isLoading = ref(false);

const winConditions = ref<TWinConditionDto[]>([]);
const selectedWinConditionId = ref<number | null>(null);
const selectedWinCondition = computed<TWinConditionDto | null>(
  () =>
    winConditions.value.find((wc) => wc.id === selectedWinConditionId.value) ??
    null
);
const winConditionIsOption = computed(
  () => selectedWinCondition.value?.condition_type === 'OPTION'
);
const winConditionIsPoints = computed(
  () => selectedWinCondition.value?.condition_type === 'POINTS'
);

const tieBreakerRequired = ref(false);
const requiredTieBreaker = ref<TTieBreakerDto | null>(null);
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
      win_condition_option: null as number | null,
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
  const selectedGame = await fetchSelectedGame(props.selectedGameId);
  gameLink.value = selectedGame.game_link ?? '';
  initialGameLink.value = gameLink.value;
  if (!selectedGame.game) return;
  resultConfig.value = await fetchResultConfigForGame(selectedGame.game);
}

function isValidGameLink(value: string) {
  const link = value.trim();
  if (!link) return true;

  try {
    const url = new URL(link);
    return (
      ['http:', 'https:'].includes(url.protocol) && Boolean(url.hostname)
    );
  } catch {
    return false;
  }
}

function validateGameLink(value: string) {
  return isValidGameLink(value) || 'Enter a valid HTTP or HTTPS link.';
}

async function loadWinConditions() {
  if (!resultConfig.value?.id) {
    winConditions.value = [];
    selectedWinConditionId.value = null;
    return;
  }
  const wcs = await fetchOrderedWinConditions(resultConfig.value.id);
  winConditions.value = wcs;
  selectedWinConditionId.value = wcs[0]?.id ?? null;
}

async function fetchFactions() {
  const selectedGame = await fetchSelectedGame(props.selectedGameId);
  if (!selectedGame.game) return;
  factions.value = (await fetchFactionsForGame(selectedGame.game)) as Faction[];
}

async function fetchExistingResults() {
  // The guard used to sit inside an `if` block, so the `seasonId` actually
  // passed to the request was never checked and could be undefined.
  const seasonId = props.league?.season || leagueStore.leagueData?.season;
  if (!seasonId) {
    console.warn('Cannot fetch existing results: season ID is missing');
    return false;
  }
  try {
    const data = await fetchMatchResults({
      seasonId,
      leagueId: props.leagueId,
      selectedGameId: props.selectedGameId,
    });
    if (data && data.length > 0) {
      // Map existing results to formData
      formData.value = members.value.map((m) => {
        const existing = data.find((r) => r.player_profile === m.profile);
        if (existing) {
          const faction_ids: Record<number, number | null> = {};
          if (existing.factions) {
            existing.factions.forEach((f) => {
              faction_ids[f.level] = f.id;
            });
          }
          return {
            player_profile: m.profile,
            selected_game: props.selectedGameId,
            points: existing.points,
            position: existing.position,
            notes: existing.notes || '',
            starting_position: existing.starting_position,
            starting_points: existing.starting_points,
            faction_ids,
            tie_breaker_value: existing.tie_breaker_value
              ? Number(existing.tie_breaker_value)
              : null,
            win_condition_option:
              (existing.win_condition_option as { id: number } | null)?.id ??
              null,
          };
        }
        return {
          player_profile: m.profile,
          selected_game: props.selectedGameId,
          points: null,
          position: null,
          notes: '',
          starting_position: null,
          starting_points: null,
          faction_ids: {},
          tie_breaker_value: null,
          win_condition_option: null,
        };
      });
      return true;
    }
  } catch (e) {
    console.error('Error fetching existing results:', e);
  }
  return false;
}

function initFormData() {
  gameLink.value = initialGameLink.value;
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
    win_condition_option: null as number | null,
  }));
  if (resultConfig.value?.has_starting_player_order) {
    preselectStartingPositions();
  }

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
        await loadWinConditions();
        const hasResults = await fetchExistingResults();
        if (!hasResults) {
          initFormData();
        }
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

function handleTieBreaker202(data: {
  required_tie_breaker?: TTieBreakerDto;
  tie_groups?: Array<{ players: number[] }>;
  tied_players?: number[];
}) {
  tieBreakerRequired.value = true;
  requiredTieBreaker.value = data?.required_tie_breaker ?? null;

  formData.value.forEach((entry) => {
    entry.tie_breaker_value = null;
  });

  const nextPlayers = new Set<number>();
  if (Array.isArray(data?.tie_groups)) {
    tieGroups.value = data.tie_groups as Array<{
      points: number | null;
      position: number | null;
      players: number[];
    }>;
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
  if (!isValidGameLink(gameLink.value)) {
    $q.notify({
      type: 'negative',
      message: 'Enter a valid HTTP or HTTPS link.',
    });
    return;
  }

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

  if (!selectedWinConditionId.value) {
    $q.notify({
      type: 'negative',
      message: 'Please select a win condition.',
    });
    return;
  }

  if (winConditionIsOption.value) {
    const missingOpt = formData.value.filter(
      (e) => e.win_condition_option == null
    );
    if (missingOpt.length) {
      $q.notify({
        type: 'negative',
        message: `Please pick an outcome for: ${missingOpt
          .map((e) => idToName(e.player_profile))
          .join(', ')}`,
      });
      return;
    }
  }

  const results: TMatchResultPayload[] = formData.value.map((entry) => {
    const selectedFactionIds = Object.values(entry.faction_ids || []).filter(
      (id) => id !== null && id !== undefined
    ) as number[];

    const res: TMatchResultPayload = {
      player_profile: entry.player_profile,
      selected_game: entry.selected_game,
      points: winConditionIsPoints.value ? entry.points : null,
      position:
        !winConditionIsPoints.value && !winConditionIsOption.value
          ? entry.position
          : null,
      notes: entry.notes || null,
      starting_position: resultConfig.value?.has_starting_player_order
        ? entry.starting_position
        : null,
      starting_points: entry.starting_points,
      faction_ids: selectedFactionIds,
      tie_breaker_value: entry.tie_breaker_value ?? null,
      win_condition_option: winConditionIsOption.value
        ? entry.win_condition_option
        : null,
    };
    return res;
  });

  const payload: TMatchResultSubmitPayload = {
    selected_game: props.selectedGameId,
    results,
    win_condition: selectedWinConditionId.value,
    game_link: gameLink.value.trim(),
  };

  if (tieBreakerRequired.value && requiredTieBreaker.value?.id) {
    payload.tiebreaker = { id: requiredTieBreaker.value.id };
  }

  try {
    const response = await submitMatchResults(payload);

    if (response.status === 201 || response.status === 200) {
      $q.notify({ type: 'positive', message: 'Result saved.' });
      emit('submitted', props.selectedGameId);
      tieBreakerRequired.value = false;
      return;
    }

    if (response.status === 202) {
      handleTieBreaker202(response.data);
      return;
    }
  } catch (err: unknown) {
    const error = err as { response?: { data?: { detail?: string } } };
    const data = error?.response?.data;
    $q.notify({
      type: 'negative',
      message: data?.detail || 'Error saving results.',
    });
  }
}
</script>

<style scoped>
.wc-card {
  background: var(--kenner-surface-subtle);
  border-radius: 10px;
}
</style>

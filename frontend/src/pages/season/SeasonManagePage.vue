<template>
  <q-page class="q-pa-md">
    <!-- Header Area -->
    <SeasonManageHeader
      :season="season"
      :season-id="seasonId"
      :is-admin="isAdmin"
      :season-has-results="seasonHasResults"
      :opening="opening"
      :filling="filling"
      :starting="starting"
      @open-season="onOpenSeason"
      @fill-leagues="onFillLeagues"
      @start-season="onStartSeason"
    />

    <!-- Error State -->
    <ErrorDisplay v-if="error && !loading" :error="error" class="q-mb-md" />

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center q-my-xl">
      <LoadingSpinner />
    </div>

    <!-- Content -->
    <div v-else-if="!error && season">
      <router-view v-if="route.name === 'league-manager'" />

      <template v-else>
        <!-- Season Info & Members -->
        <SeasonParticipantManager
          :leagues="leagues"
          :participants="participants"
          :is-admin="isAdmin"
          :removing-participant-id="removingParticipantId"
          :season-status-label="seasonStatusLabel"
          :status-color="statusColor"
          @open-add-participant="openAddParticipantDialog"
          @remove-participant="onRemoveParticipant"
        />

        <!-- Leagues List -->
        <SeasonLeaguesSection
          :leagues="leagues"
          :is-admin="isAdmin"
          @open-add-league="openAddLeagueDialog"
          @delete-league="onDeleteLeague"
        />
      </template>
    </div>

    <!-- Add Participant Dialog -->
    <AddParticipantDialog
      v-model="showAddParticipantDialog"
      :season-name="season?.name"
      :loading="addingParticipant"
      :error="addParticipantError"
      :profile-options="filteredProfileOptions"
      @add="onAddParticipant"
    />

    <!-- Add League Dialog -->
    <AddLeagueDialog
      v-model="showAddLeagueDialog"
      :season-name="season?.name"
      :loading="addingLeague"
      :error="addLeagueError"
      :initial-level="newLeagueLevel"
      :participant-options="participantOptions"
      @create="onAddLeague"
    />
  </q-page>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { storeToRefs } from 'pinia';
import {
  fetchLeaguesBySeason,
  fetchSeason,
  fetchSeasonParticipants,
  fillLeagues,
  startSeason,
  openSeason,
  addSeasonParticipant,
  removeSeasonParticipant,
} from 'src/services/seasonService';
import { createLeague, deleteLeague } from 'src/services/leagueService';
import { fetchProfiles } from 'src/services/userService';
import ErrorDisplay from 'components/base/ErrorDisplay.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import SeasonManageHeader from 'components/season/manage/SeasonManageHeader.vue';
import SeasonParticipantManager from 'components/season/manage/SeasonParticipantManager.vue';
import AddParticipantDialog from 'components/season/manage/AddParticipantDialog.vue';
import SeasonLeaguesSection from 'components/season/manage/SeasonLeaguesSection.vue';
import AddLeagueDialog from 'components/season/manage/AddLeagueDialog.vue';
import {
  TSeasonDto,
  TLeagueDto,
  TSeasonParticipantDto,
  TPlayerProfileDto,
} from 'src/types';
import { useUserStore } from 'stores/userStore';
import { useDialog } from 'src/composables/dialog';

const route = useRoute();
const { isAdmin } = storeToRefs(useUserStore());
const { setDialog } = useDialog();
const seasonId = Number(route.params.id);

const leagues = ref<TLeagueDto[]>([]);
const season = ref<TSeasonDto | null>(null);
const participants = ref<TSeasonParticipantDto[]>([]);
const loading = ref(true);
const starting = ref(false);
const opening = ref(false);
const filling = ref(false);
const error = ref<string | null>(null);

const allProfiles = ref<TPlayerProfileDto[]>([]);
const showAddParticipantDialog = ref(false);
const addingParticipant = ref(false);
const removingParticipantId = ref<number | null>(null);
const addParticipantError = ref<string | null>(null);

const showAddLeagueDialog = ref(false);
const newLeagueLevel = ref<number>(1);
const addingLeague = ref(false);
const addLeagueError = ref<string | null>(null);

const assignedParticipantIds = computed(() => {
  const ids = new Set<number>();
  leagues.value.forEach((l) => {
    (l.members || []).forEach((m) => ids.add(m.id));
  });
  return ids;
});

const availableParticipantsForLeague = computed(() => {
  return participants.value.filter(
    (p) => !assignedParticipantIds.value.has(p.id)
  );
});

const participantOptions = computed(() => {
  return availableParticipantsForLeague.value.map((p) => ({
    label:
      p.username && p.username !== p.profile_name
        ? `${p.profile_name} (@${p.username})`
        : p.profile_name,
    value: p.id,
  }));
});

const seasonHasResults = computed(() => {
  return (
    participants.value.some((p) => p.has_results) ||
    leagues.value.some((l) => l.has_results)
  );
});

const availableProfiles = computed(() => {
  const currentParticipantProfileIds = new Set(
    participants.value.map((p) => p.profile)
  );
  return allProfiles.value.filter(
    (p) => !currentParticipantProfileIds.has(p.id)
  );
});

const profileOptions = computed(() => {
  return availableProfiles.value.map((p) => ({
    label:
      p.username && p.username !== p.profile_name
        ? `${p.profile_name} (@${p.username})`
        : p.profile_name,
    value: p.id,
  }));
});

const filteredProfileOptions = computed(() => profileOptions.value);

const isSeasonCompleted = computed(() => season.value?.is_completed ?? false);

const statusColor = computed(() => {
  if (isSeasonCompleted.value) return 'grey-7';
  switch (season.value?.status) {
    case 'OPEN':
      return 'teal-6';
    case 'RUNNING':
      return 'primary';
    case 'DONE':
      return 'grey-7';
    default:
      return 'grey-6';
  }
});

const seasonStatusLabel = computed(() => {
  if (isSeasonCompleted.value) return 'COMPLETE';
  return season.value?.status || '';
});

async function load() {
  try {
    loading.value = true;
    error.value = null;
    const [seasonData, leagueData, participantData] = await Promise.all([
      fetchSeason(seasonId),
      fetchLeaguesBySeason(seasonId),
      fetchSeasonParticipants(seasonId),
    ]);
    season.value = seasonData || null;
    leagues.value = leagueData;
    participants.value = participantData;
  } catch (e: any) {
    error.value = e?.message || 'Failed to load season details.';
  } finally {
    loading.value = false;
  }
}

async function openAddParticipantDialog() {
  addParticipantError.value = null;
  showAddParticipantDialog.value = true;
  try {
    const profiles = await fetchProfiles();
    allProfiles.value = profiles;
  } catch (e: any) {
    addParticipantError.value = e?.message || 'Failed to load player profiles.';
  }
}

async function onAddParticipant(selectedProfileId: number) {
  if (!selectedProfileId || !season.value) return;
  try {
    addingParticipant.value = true;
    addParticipantError.value = null;
    await addSeasonParticipant(seasonId, selectedProfileId);
    showAddParticipantDialog.value = false;
    await load();
  } catch (e: any) {
    addParticipantError.value =
      e?.response?.data?.detail ||
      e?.response?.data?.non_field_errors?.[0] ||
      e?.message ||
      'Failed to add participant.';
  } finally {
    addingParticipant.value = false;
  }
}

function onRemoveParticipant(participant: TSeasonParticipantDto) {
  if (!season.value) return;
  if (participant.has_results) {
    error.value =
      'Cannot remove participant because match results already exist for this player in this season.';
    return;
  }
  setDialog(
    'Confirm Remove Participant',
    `Are you sure you want to remove ${participant.profile_name} from ${season.value.name}?`,
    'warning',
    async () => {
      try {
        removingParticipantId.value = participant.id;
        await removeSeasonParticipant(participant.id);
        await load();
      } catch (e: any) {
        error.value =
          e?.response?.data?.detail ||
          e?.message ||
          'Failed to remove participant.';
      } finally {
        removingParticipantId.value = null;
      }
    },
    undefined,
    'Remove'
  );
}

function openAddLeagueDialog() {
  const levels = leagues.value
    .map((l) =>
      typeof l.level === 'number' ? l.level : parseInt(String(l.level), 10)
    )
    .filter((n) => !isNaN(n));
  newLeagueLevel.value = levels.length ? Math.max(...levels) + 1 : 1;
  addLeagueError.value = null;
  showAddLeagueDialog.value = true;
}

async function onAddLeague(payload: { level: number; member_ids: number[] }) {
  if (!season.value) return;
  try {
    addingLeague.value = true;
    addLeagueError.value = null;
    await createLeague({
      season: seasonId,
      level: payload.level,
      member_ids: payload.member_ids,
      status: 'PLAYING',
    });
    showAddLeagueDialog.value = false;
    await load();
  } catch (e: any) {
    addLeagueError.value =
      e?.response?.data?.detail ||
      e?.response?.data?.non_field_errors?.[0] ||
      e?.message ||
      'Failed to create league.';
  } finally {
    addingLeague.value = false;
  }
}

function onDeleteLeague(league: TLeagueDto) {
  if (!season.value) return;
  if (league.has_results) {
    error.value = `Cannot remove League ${league.level} because match results already exist in it.`;
    return;
  }
  setDialog(
    'Confirm Delete League',
    `Are you sure you want to remove League ${league.level} from ${season.value.name}?`,
    'warning',
    async () => {
      try {
        await deleteLeague(league.id);
        await load();
      } catch (e: any) {
        error.value =
          e?.response?.data?.detail || e?.message || 'Failed to remove league.';
      }
    },
    undefined,
    'Delete'
  );
}

async function onFillLeagues() {
  if (!season.value) return;

  setDialog(
    'Confirm Fill Leagues',
    `Are you sure you want to distribute the current participants of ${season.value.name} into leagues? This will replace any existing leagues for this season.`,
    'warning',
    async () => {
      try {
        filling.value = true;
        await fillLeagues(seasonId);
        await load();
      } catch (e: any) {
        error.value =
          e?.response?.data?.detail || e?.message || 'Failed to fill leagues.';
      } finally {
        filling.value = false;
      }
    },
    undefined,
    'Fill Leagues'
  );
}

async function onOpenSeason() {
  if (!season.value) return;

  setDialog(
    'Confirm Open Season for Registration',
    `Are you sure you want to open ${season.value.name} for registration? This will announce registration to all users.`,
    'warning',
    async () => {
      try {
        opening.value = true;
        await openSeason(seasonId);
        await load();
      } catch (e: any) {
        error.value =
          e?.response?.data?.detail ||
          e?.message ||
          'Failed to open season for registration.';
      } finally {
        opening.value = false;
      }
    },
    undefined,
    'Open Season'
  );
}

async function onStartSeason() {
  if (!season.value) return;

  setDialog(
    'Confirm Manual Start',
    `Are you sure you want to start ${season.value.name} manually? This will close the currently running season if any.`,
    'warning',
    async () => {
      try {
        starting.value = true;
        await startSeason(seasonId);
        await load();
      } catch (e: any) {
        error.value =
          e?.response?.data?.detail || e?.message || 'Failed to start season.';
      } finally {
        starting.value = false;
      }
    },
    undefined,
    'Start Season'
  );
}

onMounted(load);
</script>

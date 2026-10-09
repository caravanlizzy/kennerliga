<template>
  <q-page class="q-pa-md">
    <!-- Header Area -->
    <div v-if="route.name !== 'league-manager'" class="row items-center justify-between q-mb-md">
      <div class="text-h5 text-weight-bold text-dark tracking-tight">
        {{ season?.name || '…' }}
      </div>
      <div class="row items-center q-gutter-x-sm">
        <KennerButton
          outline
          no-caps
          icon="visibility"
          round
          color="secondary"
          size="sm"
          :to="{ name: 'season-overview', params: { id: seasonId } }"
        >
          <KennerTooltip>View Public Overview</KennerTooltip>
        </KennerButton>
        <KennerButton
          v-if="isAdmin && season?.status === 'OPEN'"
          outline
          no-caps
          icon="groups"
          round
          color="secondary"
          size="sm"
          :loading="filling"
          :disable="seasonHasResults"
          @click="onFillLeagues"
        >
          <KennerTooltip>
            {{ seasonHasResults ? 'Cannot refill leagues: match results already exist in this season' : 'Fill Leagues from current participants' }}
          </KennerTooltip>
        </KennerButton>
        <KennerButton
          v-if="isAdmin && season?.status === 'OPEN'"
          outline
          no-caps
          icon="play_arrow"
          round
          color="positive"
          size="sm"
          :loading="starting"
          @click="onStartSeason"
        >
          <KennerTooltip>Start Season Manually</KennerTooltip>
        </KennerButton>
      </div>
    </div>

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
        <div class="season-summary q-mb-lg">
          <div class="season-summary__header row items-center q-gutter-x-sm q-px-md q-py-sm">
            <div class="stat-pill">{{ leagues.length }} leagues</div>
            <div class="stat-pill">{{ participants.length }} players</div>
            <div
              v-if="seasonStatusLabel"
              class="status-pill"
              :class="`status-pill--${statusColor}`"
            >
              {{ seasonStatusLabel }}
            </div>
          </div>

          <div class="season-summary__divider" />

          <q-expansion-item
            label="Show participants"
            header-class="text-grey-7"
            dense
            expand-icon-class="text-grey-7"
          >
            <div class="q-px-md q-pt-sm q-pb-md">
              <div v-if="isAdmin" class="row justify-end q-mb-sm">
                <KennerButton
                  outline
                  no-caps
                  size="sm"
                  color="primary"
                  icon="person_add"
                  label="Add Participant"
                  @click="openAddParticipantDialog"
                />
              </div>

              <div v-if="participants.length > 0">
                <div
                  v-for="group in participantsByLeague"
                  :key="group.league?.id || 'unassigned'"
                  class="q-mb-md"
                >
                  <div class="row items-center q-gutter-x-sm q-mb-xs">
                    <template v-if="group.league">
                      <LeagueLevel :level="group.league.level" size="20px" font-size="10px" />
                      <span class="text-caption text-weight-bold">League {{ group.league.level }}</span>
                    </template>
                    <template v-else>
                      <q-icon name="help_outline" size="16px" color="grey-6" />
                      <span class="text-caption text-weight-bold text-grey-6">Unassigned</span>
                    </template>
                    <div class="text-caption text-grey-6">({{ group.members.length }})</div>
                  </div>
                  <div v-if="group.members.length > 0" class="column q-gutter-y-xs q-pl-md q-mt-xs">
                    <div
                      v-for="p in group.members"
                      :key="p.id"
                      class="row items-center justify-between q-py-xs participant-row"
                    >
                      <div class="row items-center q-gutter-x-sm">
                        <div class="player-dot" />
                        <span class="text-caption text-grey-8">{{ p.profile_name }}</span>
                      </div>
                      <KennerButton
                        v-if="isAdmin"
                        flat
                        round
                        dense
                        size="xs"
                        color="negative"
                        icon="delete"
                        :disable="p.has_results"
                        :loading="removingParticipantId === p.id"
                        @click="onRemoveParticipant(p)"
                      >
                        <KennerTooltip>
                          {{ p.has_results ? 'Cannot remove: player has match results in this season' : 'Remove participant' }}
                        </KennerTooltip>
                      </KennerButton>
                    </div>
                  </div>
                  <div v-else class="text-caption text-grey-5 italic q-ml-md">No players</div>
                </div>
              </div>
              <div v-else class="text-caption text-grey-6 italic">No registered players for this season.</div>
            </div>
          </q-expansion-item>
        </div>

        <!-- Leagues List -->
        <ContentSection
          title="Leagues"
          icon="groups"
          color="accent"
          :bordered="false"
        >
          <template #header-extra>
            <KennerButton
              v-if="isAdmin"
              outline
              no-caps
              size="sm"
              color="accent"
              icon="add"
              label="Add League"
              class="q-ml-md"
              @click="openAddLeagueDialog"
            />
          </template>

          <div v-if="leagues.length === 0" class="text-grey-7 q-pa-md bg-grey-1 rounded-borders text-center column items-center q-gutter-y-sm">
            <div>No leagues found for this season.</div>
            <KennerButton
              v-if="isAdmin"
              no-caps
              size="sm"
              color="accent"
              icon="add"
              label="Add League"
              @click="openAddLeagueDialog"
            />
          </div>
          <q-list v-else separator class="league-list-container">
            <LeagueList
              v-for="league in leagues"
              :key="league.id"
              :league="league"
              @delete="onDeleteLeague"
            />
          </q-list>
        </ContentSection>
      </template>
    </div>

    <!-- Add Participant Dialog -->
    <q-dialog v-model="showAddParticipantDialog">
      <q-card style="min-width: 320px; max-width: 480px; width: 100%; border-radius: 16px" class="q-pa-md">
        <q-card-section class="row items-center justify-between q-pb-none">
          <div class="text-subtitle1 text-weight-bold">Add Participant</div>
          <q-btn v-close-popup icon="close" flat round dense color="grey-6" />
        </q-card-section>

        <q-card-section class="q-pt-sm">
          <p class="text-caption text-grey-7 q-mb-md">
            Select a player to register for {{ season?.name }}.
          </p>

          <ErrorDisplay v-if="addParticipantError" :error="addParticipantError" class="q-mb-sm" />

          <KennerSelect
            v-model="selectedProfileId"
            :options="filteredProfileOptions"
            label="Select player profile"
            option-label="label"
            option-value="value"
            emit-value
            map-options
            use-input
            input-debounce="0"
            @filter="filterProfiles"
          >
            <template #no-option>
              <q-item>
                <q-item-section class="text-grey">
                  No matching players available
                </q-item-section>
              </q-item>
            </template>
          </KennerSelect>
        </q-card-section>

        <q-card-actions align="right" class="q-pt-md">
          <KennerButton flat no-caps label="Cancel" color="grey-7" v-close-popup />
          <KennerButton
            no-caps
            label="Add Player"
            color="primary"
            :loading="addingParticipant"
            :disable="!selectedProfileId"
            @click="onAddParticipant"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Add League Dialog -->
    <q-dialog v-model="showAddLeagueDialog">
      <q-card style="min-width: 320px; max-width: 480px; width: 100%; border-radius: 16px" class="q-pa-md">
        <q-card-section class="row items-center justify-between q-pb-none">
          <div class="text-subtitle1 text-weight-bold">Add League</div>
          <q-btn v-close-popup icon="close" flat round dense color="grey-6" />
        </q-card-section>

        <q-card-section class="q-pt-sm column q-gutter-y-sm">
          <p class="text-caption text-grey-7 q-mb-xs">
            Create a new league for {{ season?.name }}.
          </p>

          <ErrorDisplay v-if="addLeagueError" :error="addLeagueError" class="q-mb-sm" />

          <KennerInput
            v-model.number="newLeagueLevel"
            type="number"
            label="League Level (e.g. 1)"
          />

          <KennerSelect
            v-model="newLeagueMemberIds"
            :options="participantOptions"
            label="Select participants (optional)"
            option-label="label"
            option-value="value"
            emit-value
            map-options
            multiple
            use-chips
          >
            <template #no-option>
              <q-item>
                <q-item-section class="text-grey">
                  No participants registered for this season yet
                </q-item-section>
              </q-item>
            </template>
          </KennerSelect>
        </q-card-section>

        <q-card-actions align="right" class="q-pt-md">
          <KennerButton flat no-caps label="Cancel" color="grey-7" v-close-popup />
          <KennerButton
            no-caps
            label="Create League"
            color="accent"
            :loading="addingLeague"
            :disable="!newLeagueLevel"
            @click="onAddLeague"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import {
  fetchLeaguesBySeason,
  fetchSeason,
  fetchSeasonParticipants,
  fillLeagues,
  startSeason,
  addSeasonParticipant,
  removeSeasonParticipant,
} from 'src/services/seasonService';
import {
  createLeague,
  deleteLeague,
} from 'src/services/leagueService';
import { fetchProfiles } from 'src/services/userService';
import LeagueList from 'components/season/LeagueList.vue';
import LeagueLevel from 'components/season/LeagueLevel.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerInput from 'components/base/KennerInput.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import ContentSection from 'components/base/ContentSection.vue';
import ErrorDisplay from 'components/base/ErrorDisplay.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import { TSeasonDto, TLeagueDto, TSeasonParticipantDto, TPlayerProfileDto } from 'src/types';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
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
const filling = ref(false);
const error = ref<string | null>(null);

const allProfiles = ref<TPlayerProfileDto[]>([]);
const showAddParticipantDialog = ref(false);
const selectedProfileId = ref<number | null>(null);
const addingParticipant = ref(false);
const removingParticipantId = ref<number | null>(null);
const addParticipantError = ref<string | null>(null);

const showAddLeagueDialog = ref(false);
const newLeagueLevel = ref<number>(1);
const newLeagueMemberIds = ref<number[]>([]);
const addingLeague = ref(false);
const addLeagueError = ref<string | null>(null);

const participantOptions = computed(() => {
  return participants.value.map((p) => ({
    label: p.username && p.username !== p.profile_name
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
  const currentParticipantProfileIds = new Set(participants.value.map((p) => p.profile));
  return allProfiles.value.filter((p) => !currentParticipantProfileIds.has(p.id));
});

const profileOptions = computed(() => {
  return availableProfiles.value.map((p) => ({
    label: p.username && p.username !== p.profile_name
      ? `${p.profile_name} (@${p.username})`
      : p.profile_name,
    value: p.id,
  }));
});

const filteredProfileOptions = ref<{ label: string; value: number }[]>([]);

function filterProfiles(val: string, update: (callbackFn: () => void) => void) {
  update(() => {
    const needle = val.toLowerCase().trim();
    if (!needle) {
      filteredProfileOptions.value = profileOptions.value;
    } else {
      filteredProfileOptions.value = profileOptions.value.filter((v) =>
        v.label.toLowerCase().includes(needle)
      );
    }
  });
}

async function openAddParticipantDialog() {
  selectedProfileId.value = null;
  addParticipantError.value = null;
  showAddParticipantDialog.value = true;
  try {
    const profiles = await fetchProfiles();
    allProfiles.value = profiles;
    filteredProfileOptions.value = profileOptions.value;
  } catch (e: any) {
    addParticipantError.value = e?.message || 'Failed to load player profiles.';
  }
}

async function onAddParticipant() {
  if (!selectedProfileId.value || !season.value) return;
  try {
    addingParticipant.value = true;
    addParticipantError.value = null;
    await addSeasonParticipant(seasonId, selectedProfileId.value);
    showAddParticipantDialog.value = false;
    selectedProfileId.value = null;
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
    error.value = 'Cannot remove participant because match results already exist for this player in this season.';
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
          e?.response?.data?.detail || e?.message || 'Failed to remove participant.';
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
    .map((l) => (typeof l.level === 'number' ? l.level : parseInt(String(l.level), 10)))
    .filter((n) => !isNaN(n));
  newLeagueLevel.value = levels.length ? Math.max(...levels) + 1 : 1;
  newLeagueMemberIds.value = [];
  addLeagueError.value = null;
  showAddLeagueDialog.value = true;
}

async function onAddLeague() {
  if (!season.value) return;
  try {
    addingLeague.value = true;
    addLeagueError.value = null;
    await createLeague({
      season: seasonId,
      level: newLeagueLevel.value,
      member_ids: newLeagueMemberIds.value,
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

const participantsByLeague = computed(() => {
  const groups: { league: TLeagueDto | null; members: TSeasonParticipantDto[] }[] = [];

  const sortedLeagues = [...leagues.value].sort((a, b) => {
    const levelA = typeof a.level === 'string' ? parseInt(a.level) : a.level;
    const levelB = typeof b.level === 'string' ? parseInt(b.level) : b.level;
    return levelA - levelB;
  });

  const assignedParticipantIds = new Set<number>();

  sortedLeagues.forEach((l) => {
    const members = l.members || [];
    members.forEach((m) => assignedParticipantIds.add(m.id));
    groups.push({ league: l, members });
  });

  const unassigned = participants.value.filter((p) => !assignedParticipantIds.has(p.id));
  if (unassigned.length > 0) {
    groups.push({ league: null, members: unassigned });
  }

  return groups;
});

const statusColor = computed(() => {
  if (isSeasonCompleted.value) return 'grey-7';
  switch (season.value?.status) {
    case 'OPEN': return 'teal-6';
    case 'RUNNING': return 'primary';
    case 'DONE': return 'grey-7';
    default: return 'grey-6';
  }
});

const isSeasonCompleted = computed(() => season.value?.is_completed ?? false);

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
      fetchSeasonParticipants(seasonId)
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
        error.value = e?.response?.data?.detail || e?.message || 'Failed to fill leagues.';
      } finally {
        filling.value = false;
      }
    },
    undefined,
    'Fill Leagues'
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
        error.value = e?.response?.data?.detail || e?.message || 'Failed to start season.';
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

<style scoped lang="scss">
.season-summary {
  background: var(--kenner-bg-glass-card);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--kenner-border-color);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(54, 64, 88, 0.04);
  overflow: hidden;
}

.season-summary__header {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.6) 0%, rgba(255, 255, 255, 0.2) 100%);

  .body--dark & {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.04) 0%, rgba(255, 255, 255, 0.01) 100%);
  }
}

.season-summary__divider {
  height: 1px;
  background: linear-gradient(to right, transparent 0%, rgba(54, 64, 88, 0.1) 50%, transparent 100%);

  .body--dark & {
    background: linear-gradient(to right, transparent 0%, rgba(255, 255, 255, 0.12) 50%, transparent 100%);
  }
}

.stat-pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(54, 64, 88, 0.06);
  color: var(--kenner-text-secondary);
  font-size: 12px;
  font-weight: 600;

  .body--dark & {
    background: var(--kenner-hover-bg);
  }
}

.status-pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
  border: 1px solid transparent;
  text-transform: uppercase;
}

.status-pill--primary {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0.05) 100%);
  color: var(--q-primary);
  border-color: rgba(99, 102, 241, 0.25);
}

.status-pill--teal-6 {
  background: linear-gradient(135deg, rgba(0, 150, 136, 0.15) 0%, rgba(0, 150, 136, 0.05) 100%);
  color: #00897b;
  border-color: rgba(0, 150, 136, 0.25);

  .body--dark & {
    color: #4db6ac;
  }
}

.status-pill--grey-7,
.status-pill--grey-6 {
  background: rgba(54, 64, 88, 0.06);
  color: var(--kenner-text-secondary);
  border-color: rgba(54, 64, 88, 0.12);

  .body--dark & {
    background: var(--kenner-hover-bg);
    border-color: var(--kenner-border-color);
  }
}

.player-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--q-primary);
  opacity: 0.6;
}

.participant-row {
  border-radius: 8px;
  padding-left: 8px;
  padding-right: 8px;
  transition: background-color 0.2s ease;

  &:hover {
    background: rgba(54, 64, 88, 0.04);

    .body--dark & {
      background: var(--kenner-hover-bg);
    }
  }
}

</style>

<template>
  <q-page class="season-overview-page q-pa-md">
    <!-- Top Bar / Breadcrumb Navigation -->
    <div class="row items-center justify-between q-mb-md">
      <div class="row items-center q-gutter-x-sm">
        <KennerButton
          flat
          round
          dense
          icon="arrow_back"
          color="grey-7"
          :to="{ name: 'seasons' }"
        >
          <KennerTooltip>Back to Seasons</KennerTooltip>
        </KennerButton>
        <div class="column">
          <div class="row items-center q-gutter-x-sm">
            <h1 class="text-h5 text-weight-bolder text-dark tracking-tight q-my-none">
              {{ seasonTitle }}
            </h1>
            <q-badge
              v-if="seasonStatusLabel"
              :color="statusColor"
              class="q-px-sm q-py-xs text-weight-bold text-caption text-uppercase"
              rounded
            >
              {{ seasonStatusLabel }}
            </q-badge>
          </div>
          <div v-if="seasonSubtitle" class="text-caption text-grey-6">
            {{ seasonSubtitle }}
          </div>
        </div>
      </div>

      <!-- Action buttons -->
      <div class="row items-center q-gutter-x-sm">
        <KennerButton
          v-if="isAdmin"
          outline
          color="secondary"
          icon="settings"
          :label="isMobile ? undefined : 'Manage Season'"
          :to="{ name: 'season-manage', params: { id: seasonId } }"
        />
      </div>
    </div>

    <!-- Error State -->
    <ErrorDisplay v-if="error && !loading" :error="error" class="q-mb-md" />

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center q-my-xl">
      <LoadingSpinner text="Loading season overview..." />
    </div>

    <!-- Main Content -->
    <div v-else-if="!error && season" class="overview-content column q-gutter-y-lg">
      <!-- Season KPI Summary Banner -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-icon-wrapper bg-primary-1 text-primary">
            <q-icon name="military_tech" size="24px" />
          </div>
          <div class="kpi-info">
            <div class="kpi-value text-primary">{{ sortedLeagues.length }}</div>
            <div class="kpi-label">Total Leagues</div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon-wrapper bg-teal-1 text-teal-8">
            <q-icon name="groups" size="24px" />
          </div>
          <div class="kpi-info">
            <div class="kpi-value text-teal-8">{{ participants.length }}</div>
            <div class="kpi-label">Participants</div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon-wrapper bg-amber-1 text-amber-9">
            <q-icon name="casino" size="24px" />
          </div>
          <div class="kpi-info">
            <div class="kpi-value text-amber-9">{{ totalPicks }}</div>
            <div class="kpi-label">Total Picks</div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon-wrapper bg-indigo-1 text-indigo-7">
            <q-icon name="sports_esports" size="24px" />
          </div>
          <div class="kpi-info">
            <div class="kpi-value text-indigo-7">{{ totalSelectedGames }}</div>
            <div class="kpi-label">Games In Play</div>
          </div>
        </div>
      </div>

      <!-- Champions Podium Section (Completed Seasons) -->
      <div v-if="isSeasonCompleted" class="champions-card q-pa-md">
        <div class="row items-center q-gutter-x-sm q-mb-md">
          <div class="champions-icon-wrap">
            <q-icon name="emoji_events" color="amber-8" size="24px" />
          </div>
          <div>
            <div class="text-subtitle1 text-weight-bold text-dark">Season Champions</div>
            <div class="text-caption text-grey-6">Podium winners and league champions</div>
          </div>
        </div>
        <SeasonWinners :season-id="seasonId" />
      </div>

      <!-- Centralized League Navigator Bar -->
      <div class="league-nav-container sticky-nav">
        <div class="row items-center justify-between no-wrap q-gutter-x-md">
          <!-- League Selection Pills / Tabs -->
          <div class="league-tabs-scroll row items-center no-wrap q-gutter-x-xs">
            <!-- All Leagues Tab -->
            <button
              type="button"
              class="league-pill-btn"
              :class="{ 'league-pill-btn--active': selectedLeagueId === 'all' }"
              @click="selectLeague('all')"
            >
              <q-icon name="grid_view" size="18px" class="q-mr-xs" />
              <span>All Leagues</span>
              <span class="pill-badge">{{ sortedLeagues.length }}</span>
            </button>

            <!-- Individual League Tabs -->
            <button
              v-for="league in sortedLeagues"
              :key="league.id"
              type="button"
              class="league-pill-btn"
              :class="{
                'league-pill-btn--active': selectedLeagueId === league.id,
                'league-pill-btn--user': isUserInLeague(league.id)
              }"
              @click="selectLeague(league.id)"
            >
              <LeagueLevel :level="league.level" badge class="q-mr-xs" />
              <span>{{ leagueDisplayName(league) }}</span>
              <span class="pill-badge">{{ getMembersForLeague(league.id).length }}</span>
              <q-icon
                v-if="isUserInLeague(league.id)"
                name="person"
                size="14px"
                class="q-ml-xs text-primary"
              >
                <KennerTooltip>You participate in this league</KennerTooltip>
              </q-icon>
            </button>
          </div>
        </div>
      </div>

      <!-- VIEW A: SPECIFIC LEAGUE VIEW -->
      <div v-if="activeLeague" class="league-focused-view column q-gutter-y-md">
        <!-- League Header Card -->
        <div class="league-header-card row items-center justify-between q-pa-md">
          <div class="row items-center q-gutter-x-md">
            <LeagueLevel :level="activeLeague.level" />
            <div>
              <div class="row items-center q-gutter-x-sm">
                <span class="text-h6 text-weight-bold text-dark">
                  {{ leagueDisplayName(activeLeague) }}
                </span>
                <q-badge
                  v-if="activeLeague.status"
                  :color="leagueStatusColor(activeLeague.status)"
                  class="text-weight-bold text-caption text-uppercase q-px-sm"
                  rounded
                >
                  {{ activeLeague.status }}
                </q-badge>
                <q-badge
                  v-if="isUserInLeague(activeLeague.id)"
                  color="primary"
                  class="text-weight-bold text-caption q-px-sm"
                  rounded
                >
                  Your League
                </q-badge>
              </div>
              <div class="text-caption text-grey-7 q-mt-xs">
                {{ activeLeagueMembers.length }} Participants · {{ activeLeaguePicksCount }} Total Picks
              </div>
            </div>
          </div>

          <!-- Member Avatars Preview -->
          <div class="row items-center q-gutter-x-xs">
            <UserAvatar
              v-for="m in activeLeagueMembers"
              :key="m.id"
              :display-username="m.username"
              :subtitle="m.profile_name"
              :shape="m.avatar_shape"
              :color="m.avatar_color"
              size="32px"
            />
          </div>
        </div>

        <!-- League View Toggle Tabs -->
        <div class="row items-center justify-between q-px-xs">
          <div class="text-overline text-grey-7 text-weight-bold">
            League Content
          </div>
          <q-btn-toggle
            v-model="activeLeagueView"
            no-caps
            rounded
            unelevated
            dense
            toggle-color="primary"
            color="grey-2"
            text-color="grey-8"
            :options="[
              { label: 'Standings Matrix', value: 'standings', icon: 'grid_view' },
              { label: 'Picks & Bans', value: 'picks', icon: 'casino' },
              { label: 'Match Results', value: 'results', icon: 'scoreboard' },
              { label: 'All Details', value: 'all', icon: 'view_agenda' },
            ]"
            @update:model-value="onViewChanged"
          />
        </div>

        <!-- Standings Matrix View -->
        <div
          v-if="activeLeagueView === 'standings' || activeLeagueView === 'all'"
          class="league-section-card"
        >
          <div class="section-title-bar row items-center justify-between q-pa-md border-bottom-subtle">
            <div class="row items-center q-gutter-x-sm">
              <q-icon name="grid_view" color="primary" size="20px" />
              <span class="text-subtitle1 text-weight-bold text-dark">Standings Matrix</span>
            </div>
          </div>
          <div class="q-pa-md">
            <LeagueStandingsMatrix
              :leagueId="activeLeague.id"
              :prefetchedData="standingsMap[activeLeague.id]"
              :level="activeLeague.level"
            />
          </div>
        </div>

        <!-- Picks & Bans View -->
        <div
          v-if="activeLeagueView === 'picks' || activeLeagueView === 'all'"
          class="league-section-card"
        >
          <div class="section-title-bar row items-center justify-between q-pa-md border-bottom-subtle">
            <div class="row items-center q-gutter-x-sm">
              <q-icon name="casino" color="amber-9" size="20px" />
              <span class="text-subtitle1 text-weight-bold text-dark">Picks &amp; Bans</span>
            </div>
          </div>
          <div class="q-pa-md">
            <PlayerCard
              v-if="activeLeagueMembers.length > 0"
              :all-members="activeLeagueMembers"
            />
            <div v-else class="q-pa-xl text-grey-6 italic text-center">
              No participant picks recorded for this league.
            </div>
          </div>
        </div>

        <!-- Match Results View -->
        <div
          v-if="activeLeagueView === 'results' || activeLeagueView === 'all'"
          class="league-section-card"
        >
          <div class="section-title-bar row items-center justify-between q-pa-md border-bottom-subtle">
            <div class="row items-center q-gutter-x-sm">
              <q-icon name="scoreboard" color="indigo-7" size="20px" />
              <span class="text-subtitle1 text-weight-bold text-dark">Match Results</span>
            </div>
          </div>
          <div class="q-pa-md">
            <LeagueMatchResults
              :leagueId="activeLeague.id"
              :show-standings="false"
            />
          </div>
        </div>
      </div>

      <!-- VIEW B: ALL LEAGUES (OVERVIEW) -->
      <div v-else class="all-leagues-view column q-gutter-y-lg">
        <!-- View Toggle for All Leagues -->
        <div class="row items-center justify-between q-px-xs">
          <div class="text-overline text-grey-7 text-weight-bold">
            Season Overview Display
          </div>
          <q-btn-toggle
            v-model="activeAllView"
            no-caps
            rounded
            unelevated
            dense
            toggle-color="primary"
            color="grey-2"
            text-color="grey-8"
            :options="[
              { label: 'League Cards', value: 'cards', icon: 'dashboard' },
              { label: 'Standings Matrix', value: 'standings', icon: 'grid_view' },
              { label: 'Picks & Bans', value: 'picks', icon: 'casino' },
              { label: 'Match Results', value: 'results', icon: 'scoreboard' },
            ]"
            @update:model-value="onViewChanged"
          />
        </div>

        <!-- 1. League Cards Grid Overview -->
        <div v-if="activeAllView === 'cards'" class="league-cards-grid">
          <div
            v-for="league in sortedLeagues"
            :key="league.id"
            class="league-overview-card"
            :class="{ 'league-overview-card--user': isUserInLeague(league.id) }"
          >
            <div class="league-card-header row items-center justify-between q-pb-sm">
              <div class="row items-center q-gutter-x-sm">
                <LeagueLevel :level="league.level" />
                <span class="text-subtitle1 text-weight-bold text-dark">
                  {{ leagueDisplayName(league) }}
                </span>
              </div>
              <q-badge
                v-if="league.status"
                :color="leagueStatusColor(league.status)"
                class="text-weight-bold text-caption text-uppercase"
                rounded
              >
                {{ league.status }}
              </q-badge>
            </div>

            <!-- Members Preview -->
            <div class="q-py-sm">
              <div class="text-caption text-grey-6 q-mb-xs">
                Participants ({{ getMembersForLeague(league.id).length }})
              </div>
              <div class="row items-center q-gutter-xs">
                <UserAvatar
                  v-for="m in getMembersForLeague(league.id)"
                  :key="m.id"
                  :display-username="m.username"
                  :subtitle="m.profile_name"
                  :shape="m.avatar_shape"
                  :color="m.avatar_color"
                  size="28px"
                />
              </div>
            </div>

            <!-- Standings Preview (Top Players) -->
            <div v-if="standingsMap[league.id]?.standings?.length" class="q-py-xs">
              <div class="text-caption text-grey-6 q-mb-xs">Top Standings</div>
              <div class="column q-gutter-y-xs">
                <div
                  v-for="(row, idx) in standingsMap[league.id].standings.slice(0, 3)"
                  :key="row.player_profile_id"
                  class="row items-center justify-between text-caption bg-grey-1 rounded-borders q-px-sm q-py-xs"
                >
                  <div class="row items-center q-gutter-x-xs no-wrap ellipsis">
                    <span class="text-weight-bold text-grey-8">{{ idx + 1 }}.</span>
                    <span class="ellipsis">{{ row.profile_name || row.username }}</span>
                  </div>
                  <div class="row items-center q-gutter-x-xs no-wrap text-weight-bold text-primary">
                    <span>{{ row.total_league_points }} pts</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Quick Action Button -->
            <div class="q-mt-md row justify-end">
              <KennerButton
                outline
                color="primary"
                dense
                no-caps
                icon-right="arrow_forward"
                label="View League"
                @click="selectLeague(league.id)"
              />
            </div>
          </div>
        </div>

        <!-- 2. Standings Matrix for All Leagues -->
        <div v-else-if="activeAllView === 'standings'" class="column q-gutter-y-lg">
          <div
            v-for="league in sortedLeagues"
            :key="league.id"
            class="league-section-card"
          >
            <div class="section-title-bar row items-center justify-between q-pa-md border-bottom-subtle">
              <div class="row items-center q-gutter-x-sm">
                <LeagueLevel :level="league.level" badge />
                <span class="text-subtitle1 text-weight-bold text-dark">
                  {{ leagueDisplayName(league) }} Standings Matrix
                </span>
              </div>
              <KennerButton
                flat
                dense
                no-caps
                color="primary"
                icon-right="chevron_right"
                label="Focus League"
                @click="selectLeague(league.id)"
              />
            </div>
            <div class="q-pa-md">
              <LeagueStandingsMatrix
                :leagueId="league.id"
                :prefetchedData="standingsMap[league.id]"
                :level="league.level"
              />
            </div>
          </div>
        </div>

        <!-- 3. Picks & Bans for All Leagues -->
        <div v-else-if="activeAllView === 'picks'" class="column q-gutter-y-lg">
          <div
            v-for="league in sortedLeagues"
            :key="league.id"
            class="league-section-card"
          >
            <div class="section-title-bar row items-center justify-between q-pa-md border-bottom-subtle">
              <div class="row items-center q-gutter-x-sm">
                <LeagueLevel :level="league.level" badge />
                <span class="text-subtitle1 text-weight-bold text-dark">
                  {{ leagueDisplayName(league) }} Picks &amp; Bans
                </span>
              </div>
              <KennerButton
                flat
                dense
                no-caps
                color="primary"
                icon-right="chevron_right"
                label="Focus League"
                @click="selectLeague(league.id)"
              />
            </div>
            <div class="q-pa-md">
              <PlayerCard
                v-if="getMembersForLeague(league.id).length > 0"
                :all-members="getMembersForLeague(league.id)"
              />
              <div v-else class="q-pa-md text-grey-6 italic text-center">
                No participant picks recorded for this league.
              </div>
            </div>
          </div>
        </div>

        <!-- 4. Match Results for All Leagues -->
        <div v-else-if="activeAllView === 'results'" class="column q-gutter-y-lg">
          <div
            v-for="league in sortedLeagues"
            :key="league.id"
            class="league-section-card"
          >
            <div class="section-title-bar row items-center justify-between q-pa-md border-bottom-subtle">
              <div class="row items-center q-gutter-x-sm">
                <LeagueLevel :level="league.level" badge />
                <span class="text-subtitle1 text-weight-bold text-dark">
                  {{ leagueDisplayName(league) }} Match Results
                </span>
              </div>
              <KennerButton
                flat
                dense
                no-caps
                color="primary"
                icon-right="chevron_right"
                label="Focus League"
                @click="selectLeague(league.id)"
              />
            </div>
            <div class="q-pa-md">
              <LeagueMatchResults
                :leagueId="league.id"
                :show-standings="false"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import {
  fetchLeaguesBySeason,
  fetchSeason,
  fetchSeasonParticipants,
} from 'src/services/seasonService';
import { fetchSeasonFullStandings } from 'src/services/standingsService';
import ErrorDisplay from 'components/base/ErrorDisplay.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import LeagueLevel from 'components/season/LeagueLevel.vue';
import LeagueStandingsMatrix from 'components/league/LeagueStandingsMatrix.vue';
import LeagueMatchResults from 'components/league/LeagueMatchResults.vue';
import PlayerCard from 'components/league/PlayerCard.vue';
import SeasonWinners from 'components/season/SeasonWinners.vue';
import UserAvatar from 'components/ui/UserAvatar.vue';
import { useUserStore } from 'stores/userStore';
import { useUpdateStore } from 'stores/updateStore';
import { useResponsive } from 'src/composables/responsive';
import type {
  TSeasonDto,
  TLeagueDto,
  TSeasonParticipantDto,
  TSeasonLeagueStandings,
} from 'src/types';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const updateStore = useUpdateStore();
const { isMobile } = useResponsive();
const { user, isAdmin } = storeToRefs(userStore);

const seasonId = Number(route.params.id);

const season = ref<TSeasonDto | null>(null);
const leagues = ref<TLeagueDto[]>([]);
const participants = ref<TSeasonParticipantDto[]>([]);
const standingsMap = ref<Record<number, TSeasonLeagueStandings>>({});
const loading = ref(true);
const error = ref<string | null>(null);

type LeagueViewMode = 'standings' | 'picks' | 'results' | 'all';
type AllViewMode = 'cards' | 'standings' | 'picks' | 'results';

// Navigation state
const selectedLeagueId = ref<number | 'all'>('all');
const activeLeagueView = ref<LeagueViewMode>('standings');
const activeAllView = ref<AllViewMode>('cards');

let unsubSeason: (() => void) | null = null;
let unsubLeague: (() => void) | null = null;

// Sort leagues by level ascending
const sortedLeagues = computed(() => {
  return [...leagues.value].sort((a, b) => Number(a.level) - Number(b.level));
});

const activeLeague = computed<TLeagueDto | null>(() => {
  if (selectedLeagueId.value === 'all') return null;
  return leagues.value.find((l) => l.id === selectedLeagueId.value) || null;
});

const activeLeagueMembers = computed<TSeasonParticipantDto[]>(() => {
  if (!activeLeague.value) return [];
  return getMembersForLeague(activeLeague.value.id);
});

const activeLeaguePicksCount = computed(() => {
  return activeLeagueMembers.value.reduce(
    (acc, m) => acc + (m.selected_games?.length || 0),
    0
  );
});

const isSeasonCompleted = computed(() => season.value?.is_completed ?? false);

const seasonTitle = computed(() => {
  if (season.value?.name) return season.value.name;
  if (season.value?.year && season.value?.month) {
    return `${season.value.year} · Season ${season.value.month}`;
  }
  return 'Season Overview';
});

const seasonSubtitle = computed(() => {
  if (season.value?.year && season.value?.month && season.value?.name) {
    return `Season ${season.value.month} of ${season.value.year}`;
  }
  return null;
});

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

const totalPicks = computed(() => {
  return participants.value.reduce(
    (acc, p) => acc + (p.selected_games?.length || 0),
    0
  );
});

const totalSelectedGames = computed(() => {
  const allGameIds = new Set<number>();
  participants.value.forEach((p) => {
    p.selected_games?.forEach((g) => {
      if (g.game) allGameIds.add(g.game);
    });
  });
  return allGameIds.size;
});

function leagueDisplayName(league: TLeagueDto): string {
  return `League ${league.level}`;
}

function leagueStatusColor(status: string): string {
  switch (status) {
    case 'PLAYING':
      return 'positive';
    case 'BANNING':
      return 'warning';
    case 'PICKING':
    case 'REPICKING':
      return 'info';
    case 'DONE':
      return 'grey-7';
    default:
      return 'grey-6';
  }
}

function getMembersForLeague(leagueId: number): TSeasonParticipantDto[] {
  return participants.value.filter((p) => {
    if (typeof p.league === 'object' && p.league !== null) {
      return p.league.id === leagueId;
    }
    return p.league === leagueId;
  });
}

function isUserInLeague(leagueId: number): boolean {
  if (!user.value) return false;
  const members = getMembersForLeague(leagueId);
  return members.some(
    (m) =>
      m.username === user.value?.username ||
      (user.value?.profile_id && m.profile === user.value.profile_id)
  );
}

function selectLeague(leagueId: number | 'all') {
  selectedLeagueId.value = leagueId;
  updateUrlQuery();
}

function onViewChanged() {
  updateUrlQuery();
}

function updateUrlQuery() {
  const query: Record<string, string> = { ...route.query } as Record<string, string>;
  if (selectedLeagueId.value === 'all') {
    query.league = 'all';
    query.view = activeAllView.value;
  } else {
    query.league = String(selectedLeagueId.value);
    query.view = activeLeagueView.value;
  }
  void router.replace({ query });
}

function initFromRouteQuery() {
  const queryLeague = route.query.league;
  const queryView = route.query.view as string | undefined;

  if (queryLeague && queryLeague !== 'all') {
    const parsedId = Number(queryLeague);
    if (!isNaN(parsedId)) {
      selectedLeagueId.value = parsedId;
    }
  } else {
    selectedLeagueId.value = 'all';
  }

  if (queryView) {
    if (selectedLeagueId.value === 'all') {
      if (['cards', 'standings', 'picks', 'results'].includes(queryView)) {
        activeAllView.value = queryView as AllViewMode;
      }
    } else {
      if (['standings', 'picks', 'results', 'all'].includes(queryView)) {
        activeLeagueView.value = queryView as LeagueViewMode;
      }
    }
  }
}

async function load() {
  try {
    loading.value = true;
    error.value = null;

    const [seasonData, leagueData, participantData, fullStandingsData] =
      await Promise.all([
        fetchSeason(seasonId),
        fetchLeaguesBySeason(seasonId),
        fetchSeasonParticipants(seasonId),
        fetchSeasonFullStandings(seasonId).catch((err) => {
          console.warn('Could not fetch full standings:', err);
          return null;
        }),
      ]);

    season.value = seasonData || null;
    leagues.value = leagueData || [];
    participants.value = participantData || [];

    const map: Record<number, TSeasonLeagueStandings> = {};
    if (fullStandingsData?.leagues) {
      fullStandingsData.leagues.forEach((l) => {
        map[l.id] = l;
      });
    }
    standingsMap.value = map;

    // Verify selectedLeagueId exists, otherwise reset to 'all'
    if (
      selectedLeagueId.value !== 'all' &&
      !leagues.value.some((l) => l.id === selectedLeagueId.value)
    ) {
      // Check if query matched by level
      const matchByLevel = leagues.value.find(
        (l) => String(l.level) === String(selectedLeagueId.value)
      );
      if (matchByLevel) {
        selectedLeagueId.value = matchByLevel.id;
      } else {
        selectedLeagueId.value = 'all';
      }
    }
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Failed to load season details.';
  } finally {
    loading.value = false;
  }
}

watch(
  () => route.params.id,
  (newId) => {
    if (newId) {
      void load();
    }
  }
);

onMounted(() => {
  initFromRouteQuery();
  void load();
  unsubSeason = updateStore.subscribe('/season/', () => void load());
  unsubLeague = updateStore.subscribe('/league/', () => void load());
});

onUnmounted(() => {
  if (unsubSeason) unsubSeason();
  if (unsubLeague) unsubLeague();
});
</script>

<style scoped lang="scss">
.season-overview-page {
  max-width: 1300px;
  margin: 0 auto;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.kpi-card {
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  }
}

.kpi-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bg-primary-1 {
  background: rgba(var(--q-primary), 0.1);
}
.bg-teal-1 {
  background: rgba(0, 150, 136, 0.1);
}
.bg-amber-1 {
  background: rgba(255, 193, 7, 0.15);
}
.bg-indigo-1 {
  background: rgba(63, 81, 181, 0.1);
}

.kpi-value {
  font-size: 1.5rem;
  font-weight: 800;
  line-height: 1.2;
}

.kpi-label {
  font-size: 0.8rem;
  color: #757575;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.champions-card {
  background: linear-gradient(135deg, #fffbf0 0%, #ffffff 100%);
  border: 1px solid rgba(255, 193, 7, 0.3);
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(255, 193, 7, 0.08);
}

.champions-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(255, 193, 7, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Centralized League Navigator Bar */
.league-nav-container {
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  padding: 10px 16px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.sticky-nav {
  position: sticky;
  top: 60px;
  z-index: 10;
  backdrop-filter: blur(8px);
}

.league-tabs-scroll {
  overflow-x: auto;
  padding-bottom: 2px;
  scrollbar-width: thin;

  &::-webkit-scrollbar {
    height: 4px;
  }
  &::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.15);
    border-radius: 4px;
  }
}

.league-pill-btn {
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: #f8f9fa;
  color: #424242;
  border-radius: 24px;
  padding: 6px 14px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
  transition: all 0.2s ease;

  &:hover {
    background: #f0f0f0;
    border-color: rgba(0, 0, 0, 0.16);
  }

  &--active {
    background: var(--q-primary) !important;
    color: white !important;
    border-color: var(--q-primary) !important;
    box-shadow: 0 2px 8px rgba(var(--q-primary), 0.3);

    .pill-badge {
      background: rgba(255, 255, 255, 0.25);
      color: white;
    }
  }

  &--user {
    border-color: rgba(var(--q-primary), 0.4);
  }
}

.pill-badge {
  background: rgba(0, 0, 0, 0.06);
  color: #616161;
  font-size: 0.75rem;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 6px;
  font-weight: 700;
}

/* League Cards Grid */
.league-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
}

.league-overview-card {
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    border-color: rgba(var(--q-primary), 0.3);
  }

  &--user {
    border-left: 4px solid var(--q-primary);
  }
}

/* Focused League View & Section Cards */
.league-header-card {
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.league-section-card {
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.section-title-bar {
  background: #fafafa;
}

.border-bottom-subtle {
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

@media (max-width: 599px) {
  .league-header-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .sticky-nav {
    top: 50px;
  }
}
</style>

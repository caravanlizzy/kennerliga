<template>
  <q-page
    class="season-overview-page"
    :class="isMobile ? 'q-pa-none' : 'q-pa-md-lg q-pa-sm-md'"
  >
    <!-- Top Bar / Breadcrumb Navigation -->
    <SeasonHeroHeader
      :season-id="seasonId"
      :season-title="seasonTitle"
      :season-status-label="seasonStatusLabel"
      :status-color="statusColor"
      :season-subtitle="seasonSubtitle"
      :leagues-count="sortedLeagues.length"
      :participants-count="participants.length"
      :is-admin="isAdmin"
      :is-mobile="isMobile"
    />

    <!-- Error State -->
    <ErrorDisplay
      v-if="error && !loading"
      :error="error"
      class="q-mb-md q-px-md"
    />

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center q-my-xl">
      <LoadingSpinner text="Loading season overview..." />
    </div>

    <!-- Main Content -->
    <div
      v-else-if="!error && season"
      class="overview-content column q-gutter-y-md q-gutter-y-sm-lg"
      :class="isMobile ? 'q-pt-sm' : ''"
    >
      <!-- Champions Podium Section (Completed Seasons) -->
      <SeasonOverviewPodium
        v-if="isSeasonCompleted"
        :season-id="seasonId"
        :is-mobile="isMobile"
      />

      <!-- Compact League & View Controls Toolbar -->
      <SeasonControlsToolbar
        :selected-league-id="selectedLeagueId"
        :league-options="leagueOptions"
        :active-all-view="activeAllView"
        :active-league-view="activeLeagueView"
        :all-view-options="allViewOptions"
        :league-view-options="leagueViewOptions"
        :is-mobile="isMobile"
        @league-selected="onLeagueSelected"
        @update:active-all-view="activeAllView = $event as AllViewMode"
        @update:active-league-view="activeLeagueView = $event as LeagueViewMode"
        @view-changed="onViewChanged"
      />

      <!-- VIEW A: SPECIFIC LEAGUE VIEW -->
      <SeasonSingleLeagueSection
        v-if="activeLeague"
        :active-league="activeLeague"
        :active-league-members="activeLeagueMembers"
        :active-league-view="activeLeagueView"
        :standings-map="standingsMap"
        :is-mobile="isMobile"
        :is-user-in-league="isUserInLeague"
        :league-display-name="leagueDisplayName"
        :league-status-color="leagueStatusColor"
        :get-member-shape="getMemberShape"
        :get-member-color="getMemberColor"
      />

      <!-- VIEW B: ALL LEAGUES (OVERVIEW) -->
      <div v-else class="all-leagues-view column q-gutter-y-md">
        <!-- 1. League Cards Grid / List Overview -->
        <SeasonLeagueCardsGrid
          v-if="activeAllView === 'cards'"
          :sorted-leagues="sortedLeagues"
          :standings-map="standingsMap"
          :is-mobile="isMobile"
          :is-user-in-league="isUserInLeague"
          :league-display-name="leagueDisplayName"
          :league-status-color="leagueStatusColor"
          :get-members-for-league="getMembersForLeague"
          :get-member-shape="getMemberShape"
          :get-member-color="getMemberColor"
          :is-current-user="isCurrentUser"
          :format-points="formatPoints"
          @select-league="selectLeague"
        />

        <!-- 2, 3, 4. All Leagues Sections (Standings, Picks, Results) -->
        <SeasonAllLeaguesSection
          v-else
          :active-all-view="activeAllView"
          :sorted-leagues="sortedLeagues"
          :standings-map="standingsMap"
          :is-mobile="isMobile"
          :is-user-in-league="isUserInLeague"
          :league-display-name="leagueDisplayName"
          :get-members-for-league="getMembersForLeague"
          @select-league="selectLeague"
        />
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
import SeasonHeroHeader from 'components/season/overview/SeasonHeroHeader.vue';
import SeasonOverviewPodium from 'components/season/overview/SeasonOverviewPodium.vue';
import SeasonControlsToolbar from 'components/season/overview/SeasonControlsToolbar.vue';
import SeasonSingleLeagueSection from 'components/season/overview/SeasonSingleLeagueSection.vue';
import SeasonLeagueCardsGrid from 'components/season/overview/SeasonLeagueCardsGrid.vue';
import SeasonAllLeaguesSection from 'components/season/overview/SeasonAllLeaguesSection.vue';
import { useUserStore } from 'stores/userStore';
import { useUpdateStore } from 'stores/updateStore';
import { useResponsive } from 'src/composables/responsive';
import { useUserProfileDisplay } from 'src/composables/userProfileDisplay';
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
const { isCurrentUser, resolveAvatarShape, resolveAvatarColor, formatPoints } =
  useUserProfileDisplay();

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

const leagueOptions = computed(() => [
  {
    label: 'All Leagues',
    value: 'all' as const,
    memberCount: sortedLeagues.value.length,
    isUser: false,
  },
  ...sortedLeagues.value.map((l) => ({
    label: leagueDisplayName(l),
    value: l.id,
    level: l.level,
    memberCount: getMembersForLeague(l.id).length,
    isUser: isUserInLeague(l.id),
  })),
]);

const leagueViewOptions = computed(() => [
  {
    label: isMobile.value ? 'Standings' : 'Standings Matrix',
    value: 'standings',
    icon: 'grid_view',
  },
  {
    label: isMobile.value ? 'Picks' : 'Picks & Bans',
    value: 'picks',
    icon: 'casino',
  },
  {
    label: isMobile.value ? 'Results' : 'Match Results',
    value: 'results',
    icon: 'scoreboard',
  },
  {
    label: isMobile.value ? 'All' : 'All Details',
    value: 'all',
    icon: 'view_agenda',
  },
]);

const allViewOptions = computed(() => [
  {
    label: isMobile.value ? 'Cards' : 'League Cards',
    value: 'cards',
    icon: 'dashboard',
  },
  {
    label: isMobile.value ? 'Standings' : 'Standings Matrix',
    value: 'standings',
    icon: 'grid_view',
  },
  {
    label: isMobile.value ? 'Picks' : 'Picks & Bans',
    value: 'picks',
    icon: 'casino',
  },
  {
    label: isMobile.value ? 'Results' : 'Match Results',
    value: 'results',
    icon: 'scoreboard',
  },
]);

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

function findParticipant(
  leagueId: number,
  playerProfileId?: number,
  username?: string
): TSeasonParticipantDto | undefined {
  const members = getMembersForLeague(leagueId);
  return members.find(
    (m) =>
      (playerProfileId !== undefined &&
        (m.profile === playerProfileId || m.id === playerProfileId)) ||
      (username && m.username === username)
  );
}

function getMemberShape(
  leagueId: number,
  playerProfileId?: number,
  username?: string
): string | undefined {
  const p = findParticipant(leagueId, playerProfileId, username);
  return resolveAvatarShape(playerProfileId, username, p?.avatar_shape);
}

function getMemberColor(
  leagueId: number,
  playerProfileId?: number,
  username?: string
): string | undefined {
  const p = findParticipant(leagueId, playerProfileId, username);
  return resolveAvatarColor(playerProfileId, username, p?.avatar_color);
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

function onLeagueSelected(leagueId: number | 'all') {
  selectedLeagueId.value = leagueId;
  updateUrlQuery();
}

function onViewChanged() {
  updateUrlQuery();
}

function updateUrlQuery() {
  const query: Record<string, string> = { ...route.query } as Record<
    string,
    string
  >;
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
    error.value =
      e instanceof Error ? e.message : 'Failed to load season details.';
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
  max-width: 1360px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
  overflow-x: hidden;
}
</style>

<template>
  <q-page class="season-overview-page" :class="isMobile ? 'q-pa-none' : 'q-pa-md-lg q-pa-sm-md'">
    <!-- Top Bar / Breadcrumb Navigation -->
    <div
      class="row items-center justify-between"
      :class="isMobile ? 'q-pa-md border-bottom-subtle' : 'q-mb-md q-mb-sm-lg'"
    >
      <div class="row items-center q-gutter-x-sm no-wrap col ellipsis">
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
        <div class="column col ellipsis">
          <div class="row items-center q-gutter-x-sm no-wrap">
            <h1 class="text-h6 text-sm-h5 text-weight-bolder text-dark tracking-tight q-my-none ellipsis">
              {{ seasonTitle }}
            </h1>
            <q-badge
              v-if="seasonStatusLabel"
              :color="statusColor"
              class="q-px-sm q-py-xs text-weight-bold text-caption text-uppercase shrink-0"
              rounded
            >
              {{ seasonStatusLabel }}
            </q-badge>
          </div>
          <div class="row items-center q-gutter-x-xs text-caption text-grey-6 ellipsis wrap q-mt-xs">
            <span v-if="seasonSubtitle">{{ seasonSubtitle }}</span>
            <span v-if="seasonSubtitle && sortedLeagues.length > 0">·</span>
            <span v-if="sortedLeagues.length > 0">
              {{ sortedLeagues.length }} {{ sortedLeagues.length === 1 ? 'League' : 'Leagues' }}
            </span>
            <span v-if="sortedLeagues.length > 0 && participants.length > 0">·</span>
            <span v-if="participants.length > 0">
              {{ participants.length }} {{ participants.length === 1 ? 'Participant' : 'Participants' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Action buttons -->
      <div class="row items-center q-gutter-x-sm shrink-0">
        <KennerButton
          v-if="isAdmin"
          outline
          color="secondary"
          icon="settings"
          :label="isMobile ? undefined : 'Manage Season'"
          :round="isMobile"
          :dense="isMobile"
          :to="{ name: 'season-manage', params: { id: seasonId } }"
        />
      </div>
    </div>

    <!-- Error State -->
    <ErrorDisplay v-if="error && !loading" :error="error" class="q-mb-md q-px-md" />

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center q-my-xl">
      <LoadingSpinner text="Loading season overview..." />
    </div>

    <!-- Main Content -->
    <div v-else-if="!error && season" class="overview-content column q-gutter-y-md q-gutter-y-sm-lg" :class="isMobile ? 'q-pt-sm' : ''">
      <!-- Champions Podium Section (Completed Seasons) -->
      <div v-if="isSeasonCompleted" class="champions-card" :class="isMobile ? 'q-mx-md q-pa-md' : 'q-pa-md q-pa-sm-lg'">
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

      <!-- Compact League & View Controls Toolbar -->
      <div
        class="controls-toolbar row items-center justify-between q-gutter-y-sm"
        :class="isMobile ? 'q-px-md' : ''"
      >
        <!-- League Selector Dropdown -->
        <div class="league-select-container" :class="isMobile ? 'full-width' : ''">
          <KennerSelect
            v-model="selectedLeagueId"
            :options="leagueOptions"
            emit-value
            map-options
            dense
            label="League"
            class="full-width"
            @update:model-value="onLeagueSelected"
          >
            <template #selected-item="scope">
              <div class="row items-center q-gutter-x-xs no-wrap ellipsis">
                <LeagueLevel
                  v-if="scope.opt.level !== undefined"
                  :level="scope.opt.level"
                  badge
                  class="q-mr-xs"
                />
                <q-icon
                  v-else
                  name="grid_view"
                  size="16px"
                  color="primary"
                  class="q-mr-xs"
                />
                <span class="ellipsis text-weight-bold">{{ scope.opt.label }}</span>
              </div>
            </template>
            <template #option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section avatar style="min-width: 32px">
                  <LeagueLevel
                    v-if="scope.opt.level !== undefined"
                    :level="scope.opt.level"
                    badge
                  />
                  <q-icon
                    v-else
                    name="grid_view"
                    size="18px"
                    color="primary"
                  />
                </q-item-section>
                <q-item-section>
                  <q-item-label class="row items-center q-gutter-x-xs">
                    <span class="text-weight-medium">{{ scope.opt.label }}</span>
                    <q-badge
                      v-if="scope.opt.isUser"
                      color="primary"
                      rounded
                      class="text-caption q-px-xs"
                    >
                      You
                    </q-badge>
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <span class="text-caption text-grey-6">
                    {{ scope.opt.value === 'all' ? `${scope.opt.memberCount} leagues` : `${scope.opt.memberCount} players` }}
                  </span>
                </q-item-section>
              </q-item>
            </template>
          </KennerSelect>
        </div>

        <!-- View Switcher Toggle -->
        <div class="view-toggle-container" :class="isMobile ? 'full-width' : ''">
          <q-btn-toggle
            v-if="selectedLeagueId === 'all'"
            v-model="activeAllView"
            no-caps
            rounded
            unelevated
            :spread="isMobile"
            class="season-view-toggle"
            toggle-color="primary"
            color="grey-2"
            text-color="grey-8"
            :options="allViewOptions"
            @update:model-value="onViewChanged"
          />
          <q-btn-toggle
            v-else
            v-model="activeLeagueView"
            no-caps
            rounded
            unelevated
            :spread="isMobile"
            class="season-view-toggle"
            toggle-color="primary"
            color="grey-2"
            text-color="grey-8"
            :options="leagueViewOptions"
            @update:model-value="onViewChanged"
          />
        </div>
      </div>

      <!-- VIEW A: SPECIFIC LEAGUE VIEW -->
      <div v-if="activeLeague" class="league-focused-view column q-gutter-y-md">
        <!-- League Header Info -->
        <div
          class="row items-center justify-between wrap q-py-sm border-bottom-subtle"
          :class="isMobile ? 'q-px-md' : 'q-px-xs'"
        >
          <div class="row items-center q-gutter-x-sm">
            <LeagueLevel :level="activeLeague.level" />
            <div>
              <div class="row items-center q-gutter-xs wrap">
                <span class="text-subtitle1 text-sm-h6 text-weight-bold text-dark">
                  {{ leagueDisplayName(activeLeague) }}
                </span>
                <q-badge
                  v-if="activeLeague.status"
                  :color="leagueStatusColor(activeLeague.status)"
                  class="text-weight-bold text-caption text-uppercase q-px-xs q-px-sm-sm"
                  rounded
                >
                  {{ activeLeague.status }}
                </q-badge>
                <q-badge
                  v-if="isUserInLeague(activeLeague.id)"
                  color="primary"
                  class="text-weight-bold text-caption q-px-xs q-px-sm-sm"
                  rounded
                >
                  Your League
                </q-badge>
              </div>
              <div class="text-caption text-grey-7 q-mt-xs">
                {{ activeLeagueMembers.length }} Participants
              </div>
            </div>
          </div>

          <!-- Member Avatars Preview -->
          <div class="row items-center wrap q-gutter-xs q-mt-xs-sm q-mt-sm-none">
            <UserAvatar
              v-for="m in activeLeagueMembers"
              :key="m.id"
              :display-username="m.username"
              :subtitle="m.profile_name"
              :shape="getMemberShape(activeLeague.id, m.profile, m.username)"
              :color="getMemberColor(activeLeague.id, m.profile, m.username)"
              :size="isMobile ? '28px' : '34px'"
            />
          </div>
        </div>

        <!-- Standings Matrix View -->
        <div
          v-if="activeLeagueView === 'standings' || activeLeagueView === 'all'"
          class="league-section"
        >
          <div
            v-if="activeLeagueView === 'all'"
            class="row items-center q-gutter-x-sm q-py-xs"
            :class="isMobile ? 'q-px-md' : 'q-px-xs'"
          >
            <q-icon name="grid_view" color="primary" size="20px" />
            <span class="text-subtitle1 text-weight-bold text-dark">Standings Matrix</span>
          </div>
          <div :class="isMobile ? 'q-px-none' : 'q-px-xs'">
            <LeagueStandingsMatrix
              :leagueId="activeLeague.id"
              :prefetchedData="standingsMap[activeLeague.id]"
              :level="activeLeague.level"
            />
          </div>
        </div>

        <q-separator v-if="activeLeagueView === 'all'" class="q-my-md" />

        <!-- Picks & Bans View -->
        <div
          v-if="activeLeagueView === 'picks' || activeLeagueView === 'all'"
          class="league-section"
        >
          <div
            v-if="activeLeagueView === 'all'"
            class="row items-center q-gutter-x-sm q-py-xs"
            :class="isMobile ? 'q-px-md' : 'q-px-xs'"
          >
            <q-icon name="casino" color="amber-9" size="20px" />
            <span class="text-subtitle1 text-weight-bold text-dark">Picks &amp; Bans</span>
          </div>
          <div :class="isMobile ? 'q-px-none' : 'q-px-xs'">
            <PlayerCard
              v-if="activeLeagueMembers.length > 0"
              :all-members="activeLeagueMembers"
            />
            <div v-else class="q-pa-lg text-grey-6 italic text-center">
              No participant picks recorded for this league.
            </div>
          </div>
        </div>

        <q-separator v-if="activeLeagueView === 'all'" class="q-my-md" />

        <!-- Match Results View -->
        <div
          v-if="activeLeagueView === 'results' || activeLeagueView === 'all'"
          class="league-section"
        >
          <div
            v-if="activeLeagueView === 'all'"
            class="row items-center q-gutter-x-sm q-py-xs"
            :class="isMobile ? 'q-px-md' : 'q-px-xs'"
          >
            <q-icon name="scoreboard" color="indigo-7" size="20px" />
            <span class="text-subtitle1 text-weight-bold text-dark">Match Results</span>
          </div>
          <div :class="isMobile ? 'q-px-none' : 'q-px-xs'">
            <LeagueMatchResults
              :leagueId="activeLeague.id"
              :show-standings="false"
            />
          </div>
        </div>
      </div>

      <!-- VIEW B: ALL LEAGUES (OVERVIEW) -->
      <div v-else class="all-leagues-view column q-gutter-y-md">
        <!-- 1. League Cards Grid / List Overview -->
        <div v-if="activeAllView === 'cards'" :class="isMobile ? 'column' : 'league-cards-grid'">
          <div
            v-for="(league, idx) in sortedLeagues"
            :key="league.id"
            :class="{
              'league-overview-card': !isMobile,
              'league-overview-card--user': !isMobile && isUserInLeague(league.id),
              'q-px-md q-py-sm': isMobile
            }"
          >
            <!-- Card Header -->
            <div class="row items-center justify-between no-wrap q-gutter-x-sm">
              <div class="row items-center q-gutter-x-xs no-wrap ellipsis col">
                <LeagueLevel :level="league.level" badge />
                <span class="text-subtitle1 text-weight-bold text-dark ellipsis">
                  {{ leagueDisplayName(league) }}
                </span>
                <q-badge
                  v-if="isUserInLeague(league.id)"
                  color="primary"
                  class="text-weight-bold text-caption q-px-xs shrink-0"
                  rounded
                >
                  You
                </q-badge>
                <q-badge
                  v-if="league.status"
                  :color="leagueStatusColor(league.status)"
                  class="text-weight-bold text-caption text-uppercase q-px-xs shrink-0"
                  rounded
                >
                  {{ league.status }}
                </q-badge>
              </div>
              <KennerButton
                outline
                dense
                no-caps
                size="sm"
                color="primary"
                icon-right="arrow_forward"
                label="View"
                class="q-px-sm shrink-0"
                @click="selectLeague(league.id)"
              />
            </div>

            <!-- League Meta -->
            <div class="row items-center q-gutter-x-md text-caption text-grey-7 q-py-xs">
              <div class="row items-center q-gutter-x-xs">
                <q-icon name="groups" size="17px" color="grey-6" />
                <span>{{ getMembersForLeague(league.id).length }} players</span>
              </div>
            </div>

            <!-- Standings Table -->
            <div v-if="standingsMap[league.id]?.standings?.length" class="column q-gutter-y-xs q-mt-xs">
              <div
                v-for="(row, rIdx) in standingsMap[league.id].standings"
                :key="row.player_profile_id"
                class="standings-mini-row row items-center justify-between no-wrap q-py-xs q-px-sm rounded-borders"
                :class="{
                  'standings-mini-row--leader': rIdx === 0,
                  'standings-mini-row--user': isCurrentUser(row.player_profile_id, row.username)
                }"
              >
                <div class="row items-center q-gutter-x-xs no-wrap ellipsis col q-mr-xs">
                  <span
                    class="rank-badge text-caption text-weight-bold shrink-0"
                    :class="rIdx === 0 ? 'text-amber-9' : 'text-grey-7'"
                  >
                    {{ rIdx + 1 }}.
                  </span>
                  <UserAvatar
                    :display-username="row.username"
                    :subtitle="row.profile_name"
                    :shape="getMemberShape(league.id, row.player_profile_id, row.username)"
                    :color="getMemberColor(league.id, row.player_profile_id, row.username)"
                    size="22px"
                  />
                  <span class="ellipsis text-caption text-weight-medium">
                    {{ row.profile_name || row.username }}
                  </span>
                </div>
                <div
                  class="text-caption text-weight-bold shrink-0"
                  :class="rIdx === 0 ? 'text-amber-10' : 'text-primary'"
                >
                  {{ formatPoints(row.total_league_points) }} pts
                </div>
              </div>
            </div>

            <!-- Fallback: Participants preview -->
            <div v-else class="column q-gutter-y-xs q-mt-xs">
              <div class="text-caption text-grey-6">Participants</div>
              <div class="row items-center wrap q-gutter-xs">
                <div
                  v-for="m in getMembersForLeague(league.id)"
                  :key="m.id"
                  class="row items-center q-gutter-x-xs bg-grey-1 rounded-borders q-px-sm q-py-xs text-caption"
                >
                  <UserAvatar
                    :display-username="m.username"
                    :subtitle="m.profile_name"
                    :shape="getMemberShape(league.id, m.profile, m.username)"
                    :color="getMemberColor(league.id, m.profile, m.username)"
                    size="22px"
                  />
                  <span class="text-weight-medium text-grey-8 ellipsis" style="max-width: 90px">
                    {{ m.profile_name || m.username }}
                  </span>
                </div>
              </div>
            </div>

            <q-separator v-if="isMobile && idx < sortedLeagues.length - 1" class="q-mt-md" />
          </div>
        </div>

        <!-- 2. Standings Matrix for All Leagues -->
        <div v-else-if="activeAllView === 'standings'" class="column">
          <div
            v-for="(league, index) in sortedLeagues"
            :key="league.id"
            class="league-standings-section"
          >
            <q-separator v-if="index > 0" class="q-my-lg" />
            <div class="row items-center justify-between q-py-sm" :class="isMobile ? 'q-px-md' : 'q-px-xs'">
              <div class="row items-center q-gutter-x-sm ellipsis col">
                <LeagueLevel :level="league.level" badge />
                <span class="text-subtitle1 text-weight-bold text-dark ellipsis">
                  {{ leagueDisplayName(league) }} Standings Matrix
                </span>
                <q-badge
                  v-if="isUserInLeague(league.id)"
                  color="primary"
                  class="text-weight-bold text-caption q-px-xs shrink-0"
                  rounded
                >
                  You
                </q-badge>
              </div>
              <KennerButton
                flat
                dense
                no-caps
                color="primary"
                icon-right="chevron_right"
                label="Focus League"
                class="shrink-0"
                @click="selectLeague(league.id)"
              />
            </div>
            <div :class="isMobile ? 'q-px-none' : 'q-px-xs'">
              <LeagueStandingsMatrix
                :leagueId="league.id"
                :prefetchedData="standingsMap[league.id]"
                :level="league.level"
              />
            </div>
          </div>
        </div>

        <!-- 3. Picks & Bans for All Leagues -->
        <div v-else-if="activeAllView === 'picks'" class="column">
          <div
            v-for="(league, index) in sortedLeagues"
            :key="league.id"
            class="league-picks-section"
          >
            <q-separator v-if="index > 0" class="q-my-lg" />
            <div class="row items-center justify-between q-py-sm" :class="isMobile ? 'q-px-md' : 'q-px-xs'">
              <div class="row items-center q-gutter-x-sm ellipsis col">
                <LeagueLevel :level="league.level" badge />
                <span class="text-subtitle1 text-weight-bold text-dark ellipsis">
                  {{ leagueDisplayName(league) }} Picks &amp; Bans
                </span>
                <q-badge
                  v-if="isUserInLeague(league.id)"
                  color="primary"
                  class="text-weight-bold text-caption q-px-xs shrink-0"
                  rounded
                >
                  You
                </q-badge>
              </div>
              <KennerButton
                flat
                dense
                no-caps
                color="primary"
                icon-right="chevron_right"
                label="Focus League"
                class="shrink-0"
                @click="selectLeague(league.id)"
              />
            </div>
            <div :class="isMobile ? 'q-px-none' : 'q-px-xs'">
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
        <div v-else-if="activeAllView === 'results'" class="column">
          <div
            v-for="(league, index) in sortedLeagues"
            :key="league.id"
            class="league-results-section"
          >
            <q-separator v-if="index > 0" class="q-my-lg" />
            <div class="row items-center justify-between q-py-sm" :class="isMobile ? 'q-px-md' : 'q-px-xs'">
              <div class="row items-center q-gutter-x-sm ellipsis col">
                <LeagueLevel :level="league.level" badge />
                <span class="text-subtitle1 text-weight-bold text-dark ellipsis">
                  {{ leagueDisplayName(league) }} Match Results
                </span>
                <q-badge
                  v-if="isUserInLeague(league.id)"
                  color="primary"
                  class="text-weight-bold text-caption q-px-xs shrink-0"
                  rounded
                >
                  You
                </q-badge>
              </div>
              <KennerButton
                flat
                dense
                no-caps
                color="primary"
                icon-right="chevron_right"
                label="Focus League"
                class="shrink-0"
                @click="selectLeague(league.id)"
              />
            </div>
            <div :class="isMobile ? 'q-px-none' : 'q-px-xs'">
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
import KennerSelect from 'components/base/KennerSelect.vue';
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
      (playerProfileId !== undefined && (m.profile === playerProfileId || m.id === playerProfileId)) ||
      (username && m.username === username)
  );
}

function getMemberShape(
  leagueId: number,
  playerProfileId?: number,
  username?: string
): string | undefined {
  if (isCurrentUser(playerProfileId, username) && user.value?.avatar_shape) {
    return user.value.avatar_shape;
  }
  const p = findParticipant(leagueId, playerProfileId, username);
  return p?.avatar_shape;
}

function getMemberColor(
  leagueId: number,
  playerProfileId?: number,
  username?: string
): string | undefined {
  if (isCurrentUser(playerProfileId, username) && user.value?.avatar_color !== undefined) {
    return user.value.avatar_color;
  }
  const p = findParticipant(leagueId, playerProfileId, username);
  return p?.avatar_color;
}

function isCurrentUser(playerProfileId?: number, username?: string): boolean {
  if (!user.value) return false;
  if (playerProfileId !== undefined && user.value.profile_id === playerProfileId) return true;
  if (username && user.value.username === username) return true;
  return false;
}

function formatPoints(pts: number | string | undefined | null): string {
  if (pts === undefined || pts === null) return '0';
  const num = Number(pts);
  if (isNaN(num)) return '0';
  return num % 1 === 0 ? num.toFixed(0) : num.toFixed(2);
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
  max-width: 1360px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
  overflow-x: hidden;
}

.champions-card {
  background: linear-gradient(135deg, #fffbf0 0%, #ffffff 100%);
  border: 1px solid rgba(255, 193, 7, 0.3);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(255, 193, 7, 0.08);

  @media (min-width: 600px) {
    border-radius: 16px;
  }
}

.champions-icon-wrap {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  background: rgba(255, 193, 7, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.controls-toolbar {
  @media (min-width: 600px) {
    gap: 16px;
  }
}

.league-select-container {
  @media (min-width: 600px) {
    min-width: 220px;
    max-width: 320px;
  }
}

.view-toggle-container {
  @media (min-width: 600px) {
    flex-shrink: 0;
  }
}

.season-view-toggle {
  padding: 2px;
  max-width: 100%;

  @media (max-width: 599px) {
    width: 100%;

    :deep(.q-btn) {
      padding: 4px 6px;
      font-size: 0.75rem;

      .q-icon {
        font-size: 15px;
        margin-right: 4px;
      }
    }
  }
}

/* League Cards Grid */
.league-cards-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
  align-content: start;
  width: 100%;

  @media (min-width: 768px) {
    grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
    gap: 20px;
  }
}

.league-overview-card {
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  padding: 14px 16px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
  min-width: 0;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;

  @media (min-width: 600px) {
    border-radius: 16px;
    padding: 18px 20px;
    gap: 14px;
  }

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
    border-color: rgba(var(--q-primary), 0.35);
  }

  &--user {
    border-left: 4px solid var(--q-primary);
  }
}

.standings-mini-row {
  background: #f8f9fa;
  border: 1px solid rgba(0, 0, 0, 0.04);
  min-height: 36px;
  padding: 5px 10px;
  border-radius: 8px;
  transition: background-color 0.15s ease;

  @media (min-width: 600px) {
    min-height: 38px;
    padding: 6px 12px;
  }

  &--leader {
    background: rgba(255, 193, 7, 0.12);
    border-color: rgba(255, 193, 7, 0.3);
  }

  &--user {
    border-color: rgba(var(--q-primary), 0.4);
    background: rgba(var(--q-primary), 0.05);
  }
}

.rank-badge {
  min-width: 20px;
  font-size: 0.8rem;

  @media (min-width: 600px) {
    min-width: 22px;
    font-size: 0.825rem;
  }
}

.border-bottom-subtle {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}
</style>

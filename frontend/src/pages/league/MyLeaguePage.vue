<template>
  <q-page class="my-league-page q-pa-md">
    <!-- Loading State -->
    <div v-if="loading && !leagueData" class="q-py-lg">
      <LoadingSpinner text="Loading league data...">
        <template #skeleton>
          <q-skeleton type="rect" height="60px" class="q-mb-md" style="border-radius: 14px" />
          <div class="row q-col-gutter-md q-mb-lg">
            <div v-for="n in 4" :key="n" class="col-6 col-md-3">
              <q-skeleton height="72px" style="border-radius: 10px" />
            </div>
          </div>
          <div class="row q-col-gutter-lg">
            <div class="col-12 col-md-6">
              <q-skeleton height="350px" style="border-radius: 16px" class="q-mb-md" />
              <q-skeleton height="250px" style="border-radius: 16px" />
            </div>
            <div class="col-12 col-md-6">
              <q-skeleton height="600px" style="border-radius: 16px" />
            </div>
          </div>
        </template>
      </LoadingSpinner>
    </div>

    <!-- Empty State: User has no active league -->
    <div v-else-if="!user?.myCurrentLeagueId" class="empty-state-wrapper q-py-xl">
      <q-card flat bordered class="empty-league-card q-pa-xl text-center">
        <div class="empty-icon-wrap q-mx-auto q-mb-md">
          <q-icon name="military_tech" size="48px" color="primary" />
        </div>
        <div class="text-h5 text-weight-bold text-dark q-mb-xs">No Active League</div>
        <div class="text-body2 text-grey-7 q-mb-lg empty-desc">
          You are not currently enrolled in an active league for this season. You can browse seasons or check back when new leagues are created.
        </div>
        <div class="row justify-center q-gutter-sm">
          <KennerButton
            label="Browse Seasons"
            icon="calendar_month"
            color="primary"
            unelevated
            :to="{ name: 'seasons' }"
          />
          <KennerButton
            label="Return Home"
            icon="home"
            outline
            color="primary"
            :to="{ name: 'home' }"
          />
        </div>
      </q-card>
    </div>

    <!-- Active League Content -->
    <div v-else class="column q-gutter-y-md">
      <!-- Top Header Card -->
      <div class="league-header-card q-pa-md">
        <div class="row items-center justify-between q-col-gutter-md">
          <div class="row items-center q-gutter-x-sm">
            <KennerButton
              round
              flat
              dense
              icon="arrow_back"
              color="grey-8"
              class="q-mr-xs"
              @click="$router.back()"
            />
            <div class="row items-center q-gutter-x-sm">
              <span class="text-h5 text-weight-bold text-dark">My League</span>
              <LeagueLevel
                v-if="leagueData?.level"
                badge
                :level="leagueData.level"
                class="level-badge"
              />
            </div>
          </div>

          <!-- Status & Actions -->
          <div class="row items-center q-gutter-sm">
            <q-chip
              dense
              :color="statusBadgeColor"
              text-color="white"
              :icon="statusBadgeIcon"
              class="text-weight-bold status-chip"
            >
              {{ statusLabel }}
            </q-chip>

            <KennerButton
              v-if="leagueData?.season"
              label="Season Overview"
              icon="visibility"
              outline
              dense
              no-caps
              class="q-px-sm"
              :to="{
                name: 'season-overview',
                params: { seasonId: leagueData.season },
              }"
            />

            <KennerButton
              round
              flat
              dense
              icon="refresh"
              color="grey-8"
              :loading="refreshing"
              @click="handleRefresh"
            >
              <q-tooltip>Refresh League Data</q-tooltip>
            </KennerButton>
          </div>
        </div>
      </div>

      <!-- KPI Summary Row -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-icon-wrapper bg-teal-1">
            <q-icon name="groups" color="teal" size="18px" />
          </div>
          <div>
            <div class="kpi-value">{{ members.length }}</div>
            <div class="kpi-label">Players</div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon-wrapper bg-indigo-1">
            <q-icon name="casino" color="indigo" size="18px" />
          </div>
          <div>
            <div class="kpi-value">{{ totalPicksCount }}</div>
            <div class="kpi-label">Picks in Play</div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon-wrapper bg-amber-1">
            <q-icon name="emoji_events" color="amber-9" size="18px" />
          </div>
          <div>
            <div class="kpi-value">{{ reportedResultsCount }} / {{ totalPicksCount }}</div>
            <div class="kpi-label">Matches Recorded</div>
          </div>
        </div>

        <div class="kpi-card" :class="{ 'kpi-card--active-turn': isMeActivePlayer }">
          <div
            class="kpi-icon-wrapper"
            :class="isMeActivePlayer ? 'bg-primary text-white' : 'bg-primary-1 text-primary'"
          >
            <q-icon :name="isMeActivePlayer ? 'bolt' : 'flag'" size="18px" />
          </div>
          <div>
            <div class="kpi-value ellipsis" style="max-width: 140px">
              <template v-if="isMeActivePlayer">Your Turn</template>
              <template v-else-if="activePlayer">{{ activePlayer.profile_name || activePlayer.username }}</template>
              <template v-else-if="leagueStatus === 'PLAYING'">Matches Live</template>
              <template v-else-if="leagueStatus === 'DONE'">Finished</template>
              <template v-else>Selection</template>
            </div>
            <div class="kpi-label">
              <template v-if="isMeActivePlayer">Action Required</template>
              <template v-else-if="turnActionText">Turn Phase</template>
              <template v-else>League Phase</template>
            </div>
          </div>
        </div>
      </div>

      <!-- Contextual Turn & Status Callout Banner -->
      <div
        v-if="isMeActivePlayer && turnActionText"
        class="turn-alert-banner turn-alert-banner--action row items-center justify-between"
      >
        <div class="row items-center no-wrap">
          <div class="turn-alert-icon-wrap q-mr-md bg-warning text-dark">
            <q-icon name="bolt" size="22px" />
          </div>
          <div>
            <div class="text-subtitle1 text-weight-bold text-dark">It's your turn to {{ turnActionText }}!</div>
            <div class="text-caption text-grey-8">
              Complete your action in the section below to proceed to the next phase.
            </div>
          </div>
        </div>
      </div>
      <div
        v-else-if="activePlayer && turnActionText"
        class="turn-alert-banner turn-alert-banner--waiting row items-center justify-between"
      >
        <div class="row items-center no-wrap">
          <div class="turn-alert-icon-wrap q-mr-md bg-blue-1 text-primary">
            <q-icon name="hourglass_empty" size="20px" />
          </div>
          <div>
            <div class="text-subtitle2 text-weight-bold text-dark">
              Waiting for {{ activePlayer.profile_name || activePlayer.username }} to {{ turnActionText }}
            </div>
            <div class="text-caption text-grey-7">
              You will be notified once it is your turn to act.
            </div>
          </div>
        </div>
      </div>

      <!-- Prominent Active Action Card (Pick Game / Ban Game) -->
      <div v-if="isMeBanningGame" class="q-mb-sm">
        <BanGameSection />
      </div>

      <div v-if="isMePickingGame" class="q-mb-sm">
        <GameSelectionSection />
      </div>

      <!-- Main Two-Column Dashboard Grid: Standings, Matches & Results, Players -->
      <div class="row q-col-gutter-lg">
        <!-- Left Column: Standings & Matches -->
        <div class="col-12 col-lg-6 column q-gutter-y-lg">
          <!-- Standings Section (Always Visible) -->
          <LeagueStandingsSection />

          <!-- Match Results Section (Always Visible) -->
          <ResultsSection />

          <!-- Match Reporting Section (Always Visible during Playing Phase) -->
          <ReportResultsSection v-if="leagueStatus === 'PLAYING'" />
        </div>

        <!-- Right Column: Players & Picks -->
        <div class="col-12 col-lg-6 column q-gutter-y-lg">
          <!-- Players, Picks and Bans Section (Always Visible) -->
          <PlayersSection />
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue';
import { storeToRefs } from 'pinia';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import KennerButton from 'components/base/KennerButton.vue';
import LeagueLevel from 'components/season/LeagueLevel.vue';
import LeagueStandingsSection from 'components/league/sections/LeagueStandingsSection.vue';
import GameSelectionSection from 'components/league/sections/GameSelectionSection.vue';
import BanGameSection from 'components/league/sections/BanGameSection.vue';
import ResultsSection from 'components/league/sections/ResultsSection.vue';
import ReportResultsSection from 'components/league/sections/ReportResultsSection.vue';
import PlayersSection from 'components/league/sections/PlayersSection.vue';
import { useUserStore } from 'stores/userStore';
import { useUpdateStore } from 'stores/updateStore';
import { useMyLeagueStore } from 'src/composables/myLeague';

const { user } = storeToRefs(useUserStore());
const myLeagueStore = useMyLeagueStore();
const {
  loading,
  refreshing,
  leagueStatus,
  leagueData,
  members,
  selectedGamesWithResults,
  activePlayer,
  isMeActivePlayer,
  isMePickingGame,
  isMeBanningGame,
} = storeToRefs(myLeagueStore);

const updateStore = useUpdateStore();
let unsubscribe: () => void;

onMounted(async () => {
  await myLeagueStore.init();

  unsubscribe = updateStore.subscribe('/league/', async () => {
    await myLeagueStore.refresh();
  });
});

onUnmounted(() => {
  if (unsubscribe) {
    unsubscribe();
  }
});

async function handleRefresh() {
  await myLeagueStore.refresh();
}

const totalPicksCount = computed(() => {
  return members.value.reduce(
    (acc, m) => acc + (m.selected_games?.length || 0),
    0
  );
});

const reportedResultsCount = computed(() => selectedGamesWithResults.value.length);

const statusBadgeColor = computed(() => {
  switch (leagueStatus.value) {
    case 'PLAYING':
      return 'positive';
    case 'BANNING':
      return 'negative';
    case 'PICKING':
    case 'REPICKING':
      return 'warning';
    case 'DONE':
      return 'grey-7';
    default:
      return 'grey-6';
  }
});

const statusBadgeIcon = computed(() => {
  switch (leagueStatus.value) {
    case 'PLAYING':
      return 'sports_esports';
    case 'BANNING':
      return 'block';
    case 'PICKING':
    case 'REPICKING':
      return 'ads_click';
    case 'DONE':
      return 'emoji_events';
    default:
      return 'info';
  }
});

const statusLabel = computed(() => {
  switch (leagueStatus.value) {
    case 'PICKING':
      return 'Selection Phase';
    case 'REPICKING':
      return 'Reselection Phase';
    case 'BANNING':
      return 'Ban Phase';
    case 'PLAYING':
      return 'Matches Live';
    case 'DONE':
      return 'Completed';
    default:
      return leagueStatus.value;
  }
});

const turnActionText = computed(() => {
  switch (leagueStatus.value) {
    case 'PICKING':
      return 'pick a game';
    case 'REPICKING':
      return 'pick again';
    case 'BANNING':
      return 'ban a game';
    default:
      return undefined;
  }
});
</script>

<style scoped lang="scss">
.my-league-page {
  max-width: 1300px;
  margin: 0 auto;
}

.league-header-card {
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 14px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.level-badge {
  font-size: 1.1rem;
}

.status-chip {
  font-size: 0.78rem;
  letter-spacing: 0.2px;
}

/* KPI Summary Cards */
.kpi-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.kpi-card {
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 10px;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  transition: all 0.2s ease;
  flex: 1 1 calc(25% - 10px);
  min-width: 160px;

  @media (max-width: 768px) {
    flex: 1 1 calc(50% - 10px);
  }

  &:hover {
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.06);
  }

  &--active-turn {
    border-color: rgba(var(--q-primary), 0.4);
    background: linear-gradient(135deg, #fffcf5 0%, #ffffff 100%);
  }
}

.kpi-icon-wrapper {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
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
.bg-blue-1 {
  background: rgba(33, 150, 243, 0.1);
}

.kpi-value {
  font-size: 1.15rem;
  font-weight: 800;
  line-height: 1.1;
  color: #212121;
}

.kpi-label {
  font-size: 0.68rem;
  color: #757575;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin-top: 2px;
}

/* Turn Alert Banners */
.turn-alert-banner {
  border-radius: 12px;
  padding: 12px 18px;
  border: 1px solid transparent;

  &--action {
    background: #fff8e1;
    border-color: #ffe082;
  }

  &--waiting {
    background: #f0f7ff;
    border-color: #bbdefb;
  }
}

.turn-alert-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* Empty State */
.empty-state-wrapper {
  max-width: 600px;
  margin: 0 auto;
}

.empty-league-card {
  border-radius: 16px;
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.empty-icon-wrap {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(var(--q-primary), 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-desc {
  max-width: 440px;
  margin: 0 auto;
  line-height: 1.5;
}
</style>

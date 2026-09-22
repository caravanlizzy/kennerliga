<template>
  <q-page class="my-league-page q-pa-md">
    <!-- Loading State -->
    <div v-if="loading && !leagueData" class="q-py-lg">
      <LoadingSpinner text="Loading league data...">
        <template #skeleton>
          <q-skeleton type="rect" height="60px" class="q-mb-lg" style="border-radius: 14px" />
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
      <!-- Consolidated Top Header Box -->
      <div class="league-header-card q-pa-md">
        <div class="row items-center justify-between q-col-gutter-sm">
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
            <q-chip
              dense
              :color="statusBadgeColor"
              text-color="white"
              :icon="statusBadgeIcon"
              class="text-weight-bold status-chip q-ml-xs"
            >
              {{ statusLabel }}
            </q-chip>
          </div>

          <!-- Actions -->
          <div class="row items-center q-gutter-sm">
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
          </div>
        </div>

        <!-- Integrated Turn & Match Status Strip -->
        <div
          v-if="isMeActivePlayer && turnActionText"
          class="header-turn-strip header-turn-strip--action row items-center justify-between q-mt-md"
        >
          <div class="row items-center no-wrap">
            <div class="turn-strip-icon-wrap bg-warning text-dark q-mr-sm">
              <q-icon name="bolt" size="18px" />
            </div>
            <div>
              <span class="text-weight-bold text-dark">It's your turn to {{ turnActionText }}!</span>
              <span class="text-caption text-grey-8 q-ml-xs gt-xs">Complete your action in the section below.</span>
            </div>
          </div>
        </div>

        <div
          v-else-if="activePlayer && turnActionText"
          class="header-turn-strip header-turn-strip--waiting row items-center no-wrap q-mt-md"
        >
          <div class="turn-strip-icon-wrap bg-blue-1 text-primary q-mr-sm">
            <q-icon name="hourglass_empty" size="16px" />
          </div>
          <div class="text-caption text-grey-8">
            Waiting for <strong class="text-dark">{{ activePlayer.profile_name || activePlayer.username }}</strong> to {{ turnActionText }}.
          </div>
        </div>

        <div
          v-else-if="leagueStatus === 'PLAYING' && totalPlayableGamesCount > 0"
          class="header-turn-strip header-turn-strip--matches row items-center justify-between q-mt-md"
        >
          <div class="row items-center no-wrap">
            <div class="turn-strip-icon-wrap bg-amber-1 text-amber-9 q-mr-sm">
              <q-icon name="emoji_events" size="16px" />
            </div>
            <div class="text-caption text-grey-8">
              Matches: <strong class="text-dark">{{ reportedResultsCount }} / {{ totalPlayableGamesCount }}</strong> recorded
            </div>
          </div>
          <q-linear-progress
            :value="totalPlayableGamesCount > 0 ? reportedResultsCount / totalPlayableGamesCount : 0"
            color="amber-8"
            track-color="amber-1"
            rounded
            style="width: 100px; height: 6px"
            class="gt-xs q-ml-md"
          />
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
  leagueStatus,
  leagueData,
  playableSelectedGames,
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

const totalPlayableGamesCount = computed(() => {
  return playableSelectedGames.value.length;
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

/* Integrated Header Turn & Status Strip */
.header-turn-strip {
  border-radius: 10px;
  padding: 8px 14px;
  border: 1px solid transparent;

  &--action {
    background: #fff8e1;
    border-color: #ffe082;
  }

  &--waiting {
    background: #f0f7ff;
    border-color: #bbdefb;
  }

  &--matches {
    background: #fdfbf7;
    border-color: rgba(255, 193, 7, 0.3);
  }
}

.turn-strip-icon-wrap {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.bg-amber-1 {
  background: rgba(255, 193, 7, 0.15);
}

.bg-blue-1 {
  background: rgba(33, 150, 243, 0.1);
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

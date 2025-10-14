<template>
  <ActionBar />

  <SideBarLayout side-title="League Standings">
    <!-- ==================== LOADING STATE ==================== -->
    <template v-if="loading">
      <LoadingSpinner text="Loading league data...">
        <template #skeleton>
          <q-skeleton type="rect" height="28px" class="q-mb-sm" />
          <q-skeleton type="text" class="q-mb-xs" />
          <q-skeleton type="text" width="70%" class="q-mb-md" />

          <div class="row q-col-gutter-md">
            <div v-for="n in 4" :key="n" class="col-12 col-sm-6 col-md-4 col-lg-3">
              <q-skeleton height="160px" square />
            </div>
          </div>
        </template>
      </LoadingSpinner>
    </template>

    <!-- ==================== NORMAL CONTENT ==================== -->
    <div v-else class="q-pa-md">
      <!-- Game Selector - shown when user needs to pick games -->
      <template v-if="isMePickingGame">
        <ContentSection
          title="Game Selection"
          color="secondary"
          :is-opened="sectionVisibilityStates['selection']"
        >
          <GameSelector
            @submit-success="updateLeagueData"
            class="q-mt-md q-pa-xs"
          />
        </ContentSection>
      </template>

      <!-- Match Results Section -->
      <template v-if="leagueStatus === 'PLAYING'">
        <ContentSection
          title="Upload Results"
          color="secondary"
          :is-opened="sectionVisibilityStates['upload']"
        >
          <MatchResultTabs />
        </ContentSection>

        <template v-if="leagueStatus === 'PLAYING' || leagueStatus === 'DONE'">
          <ContentSection
            title="Results"
            color="positive"
            :is-opened="sectionVisibilityStates['results']"
          >
            Results to be displayed here
          </ContentSection>
        </template>
      </template>

      <!-- Player Cards Grid -->
      <ContentSection
        title="Players"
        color="info"
        :is-opened="sectionVisibilityStates['players']"
      >
        <div class="row q-col-gutter-md ">
          <div
            v-for="member in members"
            :key="member.id"
            class="col-12 col-sm-6 col-md-4 col-lg-3"
          >
            <PlayerCard :member="member" />
          </div>
        </div>
      </ContentSection>
    </div>

    <template #side>
      <!-- You can also hide the sidebar while loading; if you want that, wrap with v-if="!loading" -->
      <LeagueStandings v-if="!loading" />
    </template>
  </SideBarLayout>
</template>

<script setup lang="ts">
import { onMounted, ref, watch, watchEffect } from 'vue';
import GameSelector from 'components/league/GameSelector.vue';
import { useLeagueStore } from 'stores/leagueStore';
import { storeToRefs } from 'pinia';
import PlayerCard from 'components/league/PlayerCard.vue';
import ContentSection from 'components/base/ContentSection.vue';
import { useActionBar } from 'src/composables/actionBar';
import { banGame } from 'src/services/game/banGameService';
import { useUserStore } from 'stores/userStore';
import { useDialog } from 'src/composables/dialog';
import { useQuasar } from 'quasar';
import ActionBar from 'components/ui/ActionBar.vue';
import LeagueStandings from 'components/league/LeagueStandings.vue';
import MatchResultTabs from 'components/league/MatchResultTabs.vue';
import SideBarLayout from 'layouts/SideBarLayout.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';

const league = useLeagueStore();

onMounted(() => {
  void league.init();
});

const {
  isMePickingGame,
  isMeBanningGame,
  leagueStatus,
  selectedGamesById,
  members,
  leagueId,
  loading, // 👈 global store flag
} = storeToRefs(league);
const { updateLeagueData } = league;

const { setActions, setLeadText, reset } = useActionBar();

const { user } = useUserStore();
setLeadText('Select a game to ban');
setActions(
  Object.values(selectedGamesById.value)
    .filter((selectedGame) => selectedGame.selected_by !== user?.username)
    .map((selectedGame) => ({
      name: `${selectedGame.game_name}`,
      buttonVariant: 'primary',
      callback: () => handleBanGame(selectedGame.id, selectedGame.game_name),
    }))
);

watch(isMeBanningGame, () => {
  if (isMeBanningGame.value && leagueId.value && user.username) {
    setLeadText('Select a game to ban');
    setActions(
      Object.values(selectedGamesById.value)
        .filter((game) => game.selected_by !== user?.username)
        .map((game) => ({
          name: `${game.game_name}`,
          callback: () => handleBanGame(game.id, game.game_name),
          autoReset: false,
        }))
    );
  }
});

const { setDialog } = useDialog();
const $q = useQuasar();

function handleBanGame(selectedGameId: number, gameName: string) {
  const notifyType = undefined;
  setDialog(
    'Confirm Ban',
    `Are you sure you want to ban ${gameName.toUpperCase()}?`,
    notifyType,
    async () => {
      try {
        await banGame({
          leagueId: leagueId.value,
          username: user.username,
          selectedGameId,
        });
        await updateLeagueData();
        $q.notify({
          type: notifyType,
          message: 'Banned!',
        });
      } catch (e) {
        console.log('Could not ban game', e);
      } finally {
        reset();
      }
    },
    () => {
      console.log('Ban cancelled');
    },
    'Ban'
  );
}

interface SectionVisibilityStates {
  selection: boolean;
  upload: boolean;
  results: boolean;
  players: boolean;
}

const sectionVisibilityStates = ref<SectionVisibilityStates>({
  selection: true,
  upload: false,
  results: false,
  players: true,
});

watchEffect(() => {
  switch (leagueStatus.value) {
    case 'PLAYING':
      sectionVisibilityStates.value['upload'] = true;
      sectionVisibilityStates.value['results'] = true;
      break;
    case 'DONE':
      sectionVisibilityStates.value['results'] = true;
      break;
    case 'BANNING':
      sectionVisibilityStates.value['selection'] = false;
      sectionVisibilityStates.value['players'] = true;
      break;
    case 'PICKING':
    case 'REPICKING':
      sectionVisibilityStates.value['selection'] = true;
      break;
  }
});
</script>

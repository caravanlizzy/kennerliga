<template>
  <div>
    <LeagueStatusBar />
    <!-- Game Selector - shown when user needs to pick games -->
    <template v-if="isMePickingGame">
      <ContentSection title="Game Selection" color="positive">
        <GameSelector
          @submit-success="updateLeagueData"
          class="q-mt-md q-pa-xs"
        />
      </ContentSection>

    </template>

    <!-- Match Results Section -->
    <template v-if="leagueStatus === 'PLAYING'">
      <ContentSection title="Upload Results" color="accent">
        <!-- Game Tabs for Entering Results -->
        <q-tabs
          active-color="primary"
          indicator-color="primary"
          v-model="currentFormSelectedGameId"
        >
          <q-tab
            v-for="selectedGame in selectedGamesFetchedEmpty"
            :key="selectedGame.id"
            :name="selectedGame.id"
          >
            {{ selectedGame.game_name }}
          </q-tab>
        </q-tabs>

        <!-- Match Result Entry Form -->
        <MatchResultForm
          v-if="currentFormSelectedGameId"
          @submitted="handleSubmit"
          :selected-game-id="currentFormSelectedGameId"
        />
      </ContentSection>

      <!--      <q-separator />-->
      <template v-if="leagueStatus === 'PLAYING'">
        <ContentSection title="Results" color="positive">
          <MyLeagueResults />
        </ContentSection>
      </template>
    </template>

    <!-- Player Cards Grid -->

    <ContentSection title="Players" color="primary">
      <div class="row q-col-gutter-md q-pa-md">
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
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import GameSelector from 'components/league/GameSelector.vue';
import LeagueStatusBar from 'pages/LeagueStatusBar.vue';
import { useLeagueStore } from 'stores/leagueStore';
import { storeToRefs } from 'pinia';
import MatchResultForm from 'components/league/MatchResultForm.vue';
import PlayerCard from 'components/league/PlayerCard.vue';
import MyLeagueResults from 'components/league/MyLeagueResults.vue';
import ContentSection from 'components/base/ContentSection.vue';
import { useActionBar } from 'src/composables/actionBar';
import { banGame } from 'src/services/game/banGameService';
import { useUserStore } from 'stores/userStore';
import { useDialog } from 'src/composables/dialog';
import { useQuasar } from 'quasar';

const league = useLeagueStore();

onMounted(() => {
  void league.init();
});

const {
  isMePickingGame,
  isMeBanningGame,
  leagueStatus,
  selectedGamesFetchedEmpty,
  selectedGamesById,
  members,
  leagueId
} = storeToRefs(league);
const { updateLeagueData, refreshResultsForGame } = league;

const { setActions, setDescription, reset } = useActionBar();

const { user } = useUserStore();

const currentFormSelectedGameId = ref(null);

function handleSubmit(selectedGameId: number) {
  currentFormSelectedGameId.value = null;
  refreshResultsForGame(selectedGameId);
}

setDescription('Select a game to ban')
setActions(
  Object.values(selectedGamesById.value)
    .filter((game) => game.selected_by !== user?.username)
    .map((game) => ({
      name: `${game.game_name}`,
      buttonVariant: 'accent',
      callback: () => handleBanGame(game.id, game.game_name)
    }))
)

watch(isMeBanningGame, () => {
  if (isMeBanningGame.value && leagueId.value && user.username) {
    setDescription('Select a game to ban')
    setActions(
      Object.values(selectedGamesById.value)
        .filter((game) => game.selected_by !== user?.username)
        .map((game) => ({
          name: `${game.game_name}`,
          buttonVariant: 'primary',
          callback: () => handleBanGame(game.id, game.game_name),
          autoReset: false
        }))
    )
  }
})

const { setDialog } = useDialog();
const $q = useQuasar();

function handleBanGame(gameId: number, gameName: string) {
  const notifyType = 'warning';
  setDialog(
    'Confirm Ban',
    `Are you sure you want to ban ${gameName.toUpperCase()}?`,
    notifyType,
    async () => {
      try {
        await banGame({
          leagueId: leagueId.value,
          username: user.username,
          gameId
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
      console.log('Ban cancelled')
    },
    'Ban'
  )
}

</script>

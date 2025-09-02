<template>
  <div>
    <LeagueStatusBar />
    {{banGameSelectionId}}
    <!-- Game Selector - shown when user needs to pick games -->
    <template v-if="isMePickingGame">
      <GameSelector
        @submit-success="updateLeagueData"
        class="q-mt-md q-pa-xs"
      />
    </template>

    <!-- Match Results Section -->
    <template v-if="leagueStatus === 'PLAYING'">
      <ContentSection title="Upoad Results" color="primary">
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
        <ContentSection title="Results" color="secondary">
          <MyLeagueResults />
        </ContentSection>
      </template>
    </template>

    <!-- Player Cards Grid -->

    <ContentSection title="Players" color="info">
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

const { setActions, setDescription, setSubtitle } = useActionBar();

const { user } = useUserStore();

const currentFormSelectedGameId = ref(null);

function handleSubmit(selectedGameId: number) {
  currentFormSelectedGameId.value = null;
  refreshResultsForGame(selectedGameId);
}

const banGameSelectionId = ref<number|null>(null);

watch(isMeBanningGame, () => {
  if (isMeBanningGame.value && leagueId.value && user.username) {
    setDescription('Select a game to ban');
    setActions(
      Object.values(selectedGamesById.value)
        .filter((game) => game.selected_by !== user?.username)
        .map((game) => ({
        name: `${game.game_name}`,
        buttonVariant: 'accent',
        callback: () => handleBanGame(game.id)
      }))
    );
  }
});

function handleBanGame(gameId: number) {
  if(banGameSelectionId.value === null && gameId !== null) {
    console.log('here');
    banGameSelectionId.value = gameId
    setSubtitle('Are you sure? Please click again to ban this game');
    return;
  }
  console.log('submitting ban game');
  banGame({
    leagueId: leagueId,
    username: user.username,
    gameId: gameId
  })
  banGameSelectionId.value = null;
}
</script>

<style lang="scss">
.is-active-border-accent {
  border: 2px solid rgba($accent, 0.4);
}

.is-active-border-secondary {
  border: 2px solid rgba($secondary, 0.4);
}
</style>

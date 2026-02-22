<template>
  <q-page>
    <div v-if="loading || !user" class="q-pa-md">
      <LoadingSpinner text="Loading league data...">
        <template #skeleton>
          <q-skeleton type="rect" height="28px" class="q-mb-sm" />
          <q-skeleton type="text" class="q-mb-xs" />
          <q-skeleton type="text" width="70%" class="q-mb-md" />

          <div class="row q-col-gutter-md">
            <div
              v-for="n in 4"
              :key="n"
              class="col-12 col-sm-6 col-md-4 col-lg-3"
            >
              <q-skeleton height="160px" square />
            </div>
          </div>
        </template>
      </LoadingSpinner>
    </div>

    <div v-else class="q-pa-md relative-position league-page">
      <ActionBar class="q-mb-md" />

      <ContentSection
        v-if="!loading"
        title="League Standings"
        color="info"
        icon="leaderboard"
        bordered
        expandable
        v-model:is-opened="sectionVisibilityStates['standings']"
        class="league-section"
      >
        <LeagueStandings />
      </ContentSection>

      <template v-if="isMePickingGame">
        <ContentSection
          title="Game Selection"
          color="primary"
          icon="ads_click"
          v-model:is-opened="sectionVisibilityStates['selection']"
          expandable
          bordered
          class="league-section"
        >
          <GameSelectionView
            :leagueId="leagueId"
            :profileId="user.profile.id"
            @selection-updated="(updated:TGameSelection) => updateGameSelection(updated)"
            @selectionValid="(valid: boolean ) => selectionValid = valid"
            @set-submitter="(s: TSubmitter) => submitter = s"
            @onSuccess="updateLeagueData"
          />
        </ContentSection>
      </template>

      <template v-if="leagueStatus === 'PLAYING' || leagueStatus === 'DONE'">
        <ContentSection
          title="Results"
          color="warning"
          icon="emoji_events"
          v-model:is-opened="sectionVisibilityStates['results']"
          expandable
          bordered
          class="league-section"
        >
          <div
            v-if="selectedGamesWithResults.length > 0"
            class="row q-col-gutter-md"
          >
            <div
              v-for="game in selectedGamesWithResults"
              :key="game.id"
              class="col-12"
              :class="{ 'col-md-6': selectedGamesWithResults.length > 1 }"
            >
              <q-card class="result-card" flat>
                <q-card-section class="q-pa-sm">
                  <MatchResult :selectedGame="game" display-game-name />
                </q-card-section>
              </q-card>
            </div>
          </div>
          <div v-else class="text-center q-pa-md text-grey">
            <div class="text-subtitle1">No results recorded yet</div>
            <div v-if="leagueStatus === 'PLAYING'" class="text-caption">
              Games that are finished can be reported below.
            </div>
          </div>
        </ContentSection>
      </template>

      <template v-if="leagueStatus === 'PLAYING'">
        <ContentSection
          title="Report Results"
          color="accent"
          icon="publish"
          v-model:is-opened="sectionVisibilityStates['upload']"
          expandable
          bordered
          class="league-section"
        >
          <MatchResultTabs />
        </ContentSection>
      </template>

      <ContentSection
        title="Games - Picks and Bans"
        color="secondary"
        icon="groups"
        v-model:is-opened="sectionVisibilityStates['players']"
        expandable
        bordered
        class="league-section"
      >
        <PlayerCard :all-members="members" />
      </ContentSection>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch, watchEffect } from 'vue';
import GameSelectionView from 'components/game/selectedGame/GameSelectionView.vue';
import { useLeagueStore } from 'stores/leagueStore';
import { storeToRefs } from 'pinia';
import PlayerCard from 'components/league/PlayerCard.vue';
import ContentSection from 'components/base/ContentSection.vue';
import { useActionBar } from 'src/composables/actionBar';
import { useUserStore } from 'stores/userStore';
import { useDialog } from 'src/composables/dialog';
import { useQuasar } from 'quasar';
import ActionBar from 'components/ui/ActionBar.vue';
import LeagueStandings from 'components/league/LeagueStandings.vue';
import MatchResultTabs from 'components/league/MatchResultTabs.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import { banGame } from 'src/services/gameService';
import { TGameSelection } from 'src/types';
import MatchResult from 'components/league/MatchResult.vue';
import { useUpdateStore } from 'stores/updateStore';

const { user } = storeToRefs(useUserStore());
const myLeagueStore = useLeagueStore(user.value?.myCurrentLeagueId ?? 0)();

type TSubmitter = () => Promise<void>;
let submitter: TSubmitter;

const {
  isMePickingGame,
  isMeBanningGame,
  leagueStatus,
  selectedGamesById,
  members,
  myProfileId,
  leagueId,
  loading,
  selectedGamesWithResults,
} = storeToRefs(myLeagueStore);
const { updateLeagueData } = myLeagueStore;

const { setActions, setLeadText, setSubject, setHint, reset } = useActionBar();

const gameSelection = ref<TGameSelection | null>(null);
const selectionValid = ref(false);
function updateGameSelection(newSelection: TGameSelection) {
  gameSelection.value = newSelection;
}

const { setDialog } = useDialog();
const $q = useQuasar();
const updateStore = useUpdateStore();

let unsubscribe: () => void;

function handleSkipBan() {
  setDialog(
    'Confirm Ban',
    'Are you sure you want to skip banning?',
    'dark',
    async () => {
      try {
        await banGame({
          leagueId: leagueId.value!,
          profileId: myProfileId.value,
          skip: true,
        });
        await updateLeagueData();
        $q.notify({
          type: 'dark',
          message: 'Skipped Ban!',
        });
      } catch (e) {
        console.error('Could not ban game', e);
      } finally {
        reset();
      }
    },
    () => {
      /* Ban cancelled */
    },
    'Skip Ban'
  );
}

function handleBanGame(selectedGameId: number, gameName: string) {
  setDialog(
    'Confirm Ban',
    `Are you sure you want to ban ${gameName.toUpperCase()}?`,
    'dark',
    async () => {
      try {
        await banGame({
          leagueId: leagueId.value!,
          profileId: myProfileId.value,
          selectedGameId,
        });
        await updateLeagueData();
        $q.notify({
          type: 'dark',
          message: 'Banned!',
        });
      } catch (e) {
        console.error('Could not ban game', e);
      } finally {
        reset();
      }
    },
    () => {
      /* Ban cancelled */
    },
    'Ban'
  );
}

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

function manageActionBar() {
  reset();

  switch (leagueStatus.value) {
    case 'BANNING':
      if (isMeBanningGame.value && leagueId.value && user.value?.username) {
        setLeadText('Select a game to ban');
        setActions([
          {
            name: 'No ban',
            callback: handleSkipBan,
            buttonVariant: 'dark',
            autoReset: false,
          },
          ...Object.values(selectedGamesById.value)
            .filter((game) => game.selected_by !== user.value?.username)
            .map((game) => ({
              name: `${game.game_name}`,
              callback: () => handleBanGame(game.id, game.game_name),
              buttonVariant: 'secondary',
              autoReset: false,
            })),
        ]);
      }
      break;
    case 'PICKING':
    case 'REPICKING':
      setActions([
        {
          name: 'Save',
          callback: submitGameSelection,
          disabled: !selectionValid.value,
          buttonVariant: 'primary',
        },
      ]);
      setLeadText('Confirm your game selection');
      setSubject(gameSelection.value?.game?.name);
      break;
    case 'PLAYING':
      setHint('Games that are finished can be reported below.');
      break;
  }
}

watch(
  [isMeBanningGame, leagueStatus, gameSelection, selectionValid],
  manageActionBar,
  {
    immediate: true,
    deep: true,
  }
);

async function submitGameSelection() {
  if (!submitter) return;
  try {
    await submitter();
    await updateLeagueData();
  } catch (error) {
    console.error('Error submitting game:', error);
  }
}

const sectionVisibilityStates = ref({
  standings: true,
  selection: true,
  upload: false,
  results: false,
  players: true,
});

watchEffect(() => {
  const status = leagueStatus.value;
  const hasResults = selectedGamesWithResults.value.length > 0;

  sectionVisibilityStates.value = {
    standings: hasResults,
    selection: ['PICKING', 'REPICKING'].includes(status),
    upload: status === 'PLAYING',
    results: ['PLAYING', 'DONE'].includes(status) && hasResults,
    players: true, // Always show players/picks/bans?
  };
});
</script>

<style scoped>
.league-section {
  margin-bottom: 16px;
}

.result-card {
  border-radius: 10px;
}
</style>

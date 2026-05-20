<template>
  <ContentSection
    v-if="isMePickingGame"
    title="Game Selection"
    color="primary"
    icon="ads_click"
    v-model:is-opened="isOpened"
    expandable
    bordered
    class="league-section"
  >
    <GameSelectionView
      :leagueId="leagueId!"
      :profileId="myProfileId"
      @selection-updated="(updated: TGameSelection) => (gameSelection = updated)"
      @selectionValid="(valid: boolean) => (selectionValid = valid)"
      @set-submitter="(s: TSubmitter) => (submitter = s)"
      @onSuccess="updateLeagueData"
    />
  </ContentSection>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { useQuasar } from 'quasar';
import ContentSection from 'components/base/ContentSection.vue';
import GameSelectionView from 'components/game/selectedGame/GameSelectionView.vue';
import { useMyLeagueStore } from 'src/composables/myLeague';
import { useUserStore } from 'stores/userStore';
import { useActionBar } from 'src/composables/actionBar';
import { useDialog } from 'src/composables/dialog';
import { banGame } from 'src/services/gameService';
import { TGameSelection } from 'src/types';

type TSubmitter = () => Promise<void>;

const myLeagueStore = useMyLeagueStore();
const {
  isMePickingGame,
  isMeBanningGame,
  leagueStatus,
  selectedGamesById,
  myProfileId,
  leagueId,
} = storeToRefs(myLeagueStore);
const { updateLeagueData } = myLeagueStore;

const { user } = storeToRefs(useUserStore());
const { setActions, setLeadText, setSubject, reset } = useActionBar();
const { setDialog } = useDialog();
const $q = useQuasar();

const isOpened = ref(false);
const gameSelection = ref<TGameSelection | null>(null);
const selectionValid = ref(false);
let submitter: TSubmitter | undefined;

async function submitGameSelection() {
  if (!submitter) return;
  try {
    await submitter();
    await updateLeagueData();
  } catch (error) {
    console.error('Error submitting game:', error);
  }
}

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
        $q.notify({ type: 'dark', message: 'Skipped Ban!' });
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
        $q.notify({ type: 'dark', message: 'Banned!' });
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

function manageActionBar() {
  // Only reset for statuses this component owns; other sections manage their own.
  if (
    leagueStatus.value === 'BANNING' ||
    leagueStatus.value === 'PICKING' ||
    leagueStatus.value === 'REPICKING'
  ) {
    reset();
  }

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
  }
}

watch(
  [isMeBanningGame, leagueStatus, gameSelection, selectionValid],
  manageActionBar,
  { immediate: true, deep: true }
);

watch(
  leagueStatus,
  (status) => {
    isOpened.value = ['PICKING', 'REPICKING'].includes(status);
  },
  { immediate: true }
);
</script>

<style scoped>
.league-section {
  margin-bottom: 16px;
}
</style>

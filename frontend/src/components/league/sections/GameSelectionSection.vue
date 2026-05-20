<template>
  <ContentSection
    v-if="isMePickingGame && leagueId"
    title="Game Selection"
    color="primary"
    icon="ads_click"
    v-model:is-opened="isOpened"
    expandable
    bordered
    class="league-section"
  >
    <GameSelectionView
      :leagueId="leagueId"
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
import ContentSection from 'components/base/ContentSection.vue';
import GameSelectionView from 'components/game/selectedGame/GameSelectionView.vue';
import { useMyLeagueStore } from 'src/composables/myLeague';
import { useActionBar } from 'src/composables/actionBar';
import { TGameSelection } from 'src/types';

type TSubmitter = () => Promise<void>;

// Statuses whose action-bar contents are owned by this section.
const OWNED_STATUSES = ['PICKING', 'REPICKING'] as const;
type TOwnedStatus = (typeof OWNED_STATUSES)[number];

const isOwnedStatus = (status: unknown): status is TOwnedStatus =>
  OWNED_STATUSES.includes(status as TOwnedStatus);

const myLeagueStore = useMyLeagueStore();
const { isMePickingGame, leagueStatus, myProfileId, leagueId } =
  storeToRefs(myLeagueStore);
const { updateLeagueData } = myLeagueStore;

const { setActions, setLeadText, setSubject, reset } = useActionBar();

const isOpened = ref(false);
const gameSelection = ref<TGameSelection | null>(null);
const selectionValid = ref(false);
const submitter = ref<TSubmitter>();

async function submitGameSelection() {
  if (!submitter.value) return;
  try {
    await submitter.value();
    await updateLeagueData();
  } catch (error) {
    console.error('Error submitting game:', error);
  }
}

function manageActionBar() {
  if (!isOwnedStatus(leagueStatus.value)) return;

  setActions([
    {
      name: 'Save',
      callback: submitGameSelection,
      disabled: !selectionValid.value,
      buttonVariant: 'primary',
    },
  ]);
  setLeadText('Confirm your game selection');
  setSubject(gameSelection.value?.game?.name ?? null);
}

// Re-render the action bar only when the inputs it actually depends on change.
watch(
  [leagueStatus, selectionValid, () => gameSelection.value?.game?.name],
  manageActionBar,
  { immediate: true }
);

// When leaving an owned status, clear the action bar and local state so a
// later remount doesn't start from stale values.
watch(
  leagueStatus,
  (status, prev) => {
    isOpened.value = isOwnedStatus(status);
    if (isOwnedStatus(prev) && !isOwnedStatus(status)) {
      reset();
      gameSelection.value = null;
      selectionValid.value = false;
      submitter.value = undefined;
    }
  },
  { immediate: true }
);
</script>

<style scoped>
.league-section {
  margin-bottom: 16px;
}
</style>

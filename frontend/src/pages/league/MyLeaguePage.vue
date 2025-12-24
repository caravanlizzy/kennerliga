<template>
  <SideBarLayout side-title="Standings">
    <!-- ==================== LOADING STATE ==================== -->
    <template v-if="loading || !user">
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
    </template>

    <!-- ==================== NORMAL CONTENT ==================== -->
    <div v-else class="q-pa-md relative-position league-page">
      <ActionBar class="q-mb-md" />
      {{league}}
      <template v-if="isMePickingGame">
        <ContentSection
          title="Game Selection"
          color="accent"
          :is-opened="sectionVisibilityStates['selection']"
          expandable
          bordered
          class="league-section"
        >
          <GameSelectionView
            :leagueId="leagueId"
            :profileId="user.profile.id"
            @selection-updated="(updated:TGameSelection) => updateGameSelection(updated)"
            @selectionValid="(valid: boolean ) => selectionValid = valid"
            @set-submitter="(s: () => {}) => submitter = s"
            @onSuccess="updateLeagueData"
          />
        </ContentSection>
      </template>

      <template v-if="leagueStatus === 'PLAYING' || leagueStatus === 'DONE'">
        <ContentSection
          title="Results"
          color="primary"
          :is-opened="sectionVisibilityStates['results']"
          expandable
          bordered
          class="league-section"
        >
          <div class="row q-col-gutter-md">
            <template v-for="member of members" :key="member.profile">
              <template
                v-for="game of member.selected_games ?? []"
                :key="game.id"
              >
                <div
                  v-if="hasSelectedGameResult(game.id)"
                  class="col-12"
                  :class="{ 'col-md-6': selectedGamesWithResults.length > 1 }"
                >
                  <q-card class="result-card" flat>
                    <q-card-section class="q-pa-sm">
                      <MatchResult
                        :selectedGame="game"
                        :displayGameName="true"
                      />
                    </q-card-section>
                  </q-card>
                </div>
              </template>
            </template>
          </div>
        </ContentSection>
      </template>

      <template v-if="leagueStatus === 'PLAYING'">
        <ContentSection
          title="Upload Results"
          color="secondary"
          :is-opened="sectionVisibilityStates['upload']"
          expandable
          bordered
          class="league-section"
        >
          <MatchResultTabs />
        </ContentSection>
      </template>

      <ContentSection
        title="Games - Picks and Bans"
        color="dark"
        :is-opened="sectionVisibilityStates['players']"
        expandable
        bordered
        class="league-section"
      >
        <div class="row q-col-gutter-md">
          <div
            v-for="member in members"
            :key="member.id"
            class="col-12 col-md-6"
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
import { h, ref, watch, watchEffect } from 'vue';
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
import SideBarLayout from 'layouts/SideBarLayout.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import { banGame } from 'src/services/gameService';
import { TGameSelection } from 'src/types';
import MatchResult from 'components/league/MatchResult.vue';

const { user } = storeToRefs(useUserStore());
const myLeagueStore = useLeagueStore(user.value.myCurrentLeagueId)();

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
const { updateLeagueData, hasSelectedGameResult } = myLeagueStore;

const { setActions, setLeadText, setSubject, reset } = useActionBar();

const gameSelection = ref<TGameSelection | null>(null);
const selectionValid = ref(false);
function updateGameSelection(newSelection: TGameSelection) {
  gameSelection.value = newSelection;
}

function manageActionBar() {
  switch (leagueStatus.value) {
    case 'BANNING':
      if (isMeBanningGame.value && leagueId.value && user.value?.username) {
        setLeadText('Select a game to ban');
        setActions([
          {
            name: 'No ban',
            callback: () => handleSkipBan(),
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
      setActions([
        {
          name: 'Save',
          callback: submitGameSelection,
          disabled: !selectionValid.value,
          buttonVariant: 'accent',
        },
      ]);
      setLeadText(() => h('div', 'Confirm your game selection'));
      setSubject(gameSelection.value?.game?.name);
      break;
    default:
      console.log('No case matched');
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

type TSubmitter = () => Promise<void>;
let submitter: TSubmitter;

async function submitGameSelection() {
  try {
    await submitter();
    await updateLeagueData();
  } catch (error) {
    console.error('Error submitting game:', error);
  }
}

const { setDialog } = useDialog();
const $q = useQuasar();

function handleSkipBan() {
  setDialog(
    'Confirm Ban',
    `Are you sure you want to skip banning?`,
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
        console.log('Could not ban game', e);
      } finally {
        reset();
      }
    },
    () => {
      console.log('Ban cancelled');
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

<style scoped>
.league-section {
  margin-bottom: 16px;
}

.result-card {
  border-radius: 10px;
}
</style>

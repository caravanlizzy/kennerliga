<template>
  <!-- Header -->
  <div
    v-if="!loading && league"
    class="row items-center q-mb-lg q-pa-md bg-grey-1 rounded-borders"
  >
    <div class="col-grow">
      <q-chip
        dense
        square
        color="grey-8"
        text-color="white"
        class="q-ml-xs text-weight-medium"
      >
        {{ season?.name }} · {{ season?.status }}
      </q-chip>
      <q-chip
        dense
        square
        color="primary"
        text-color="white"
        class="q-ml-xs text-weight-medium"
      >
        L {{ league.level }}
      </q-chip>
    </div>
    <div class="col-auto">
      <q-btn flat icon="refresh" round color="secondary" size="md" @click="load">
        <q-tooltip>Refresh</q-tooltip>
      </q-btn>
    </div>
  </div>

  <!-- Loading / Error -->
  <LoadingSpinner v-if="loading" />
  <ErrorDisplay v-else-if="error" :error="error" class="q-mb-md" />

  <!-- Empty state -->
  <q-card
    v-else-if="!league?.members || league.members.length === 0"
    flat
    bordered
    class="q-pa-xl flex items-center justify-center bg-grey-1"
  >
    <div class="column items-center q-pa-lg">
      <q-icon name="group_off" size="64px" color="grey-4" class="q-mb-md" />
      <div class="text-h6 text-grey-8">No members yet</div>
      <div class="text-body1 text-grey-6 q-mt-sm">
        Add members to start selecting games.
      </div>
    </div>
  </q-card>

  <!-- Members × Selected Games grid -->
  <div v-else class="row q-col-gutter-lg">
    <template v-for="member in league?.members" :key="member.id">
      <!-- Card per selected game -->
      <div
        v-for="selGame in member.selected_games || []"
        :key="`${member.id}-${selGame.id}`"
        class="col-12 col-md-6"
      >
        <q-card
          flat
          bordered
          class="fit rounded-borders overflow-hidden"
          v-if="showPlayerGrid"
        >
          <!-- Player Header Section -->
          <q-card-section class="q-pa-lg bg-grey-3">
            <div class="row items-center justify-between">
              <div class="col">
                <div class="text-h6 text-weight-bold text-grey-9">
                  <q-icon name="sports_esports" size="sm" class="q-mr-sm" />
                  {{ selGame?.game_name || 'No Game Selected' }}
                </div>
              </div>

              <div class="col-auto row items-center q-gutter-md">
                <q-badge color="dark" text-color="white">
                  <q-icon name="person" size="xs" class="q-mr-xs" />
                  <span class="text-weight-medium">{{ member.profile_name }}</span>
                </q-badge>

                <div
                  v-if="
                    ['PICKING', 'REPICKING', 'BANNING'].includes(league.status) &&
                    season?.status === 'RUNNING'
                  "
                >
                  <q-badge
                    v-if="member.profile === league.active_player"
                    color="positive"
                    text-color="white"
                    class="q-py-xs q-px-sm"
                  >
                    <q-icon size="xs" name="star" class="q-mr-xs" />
                    <span class="text-weight-bold">Active</span>
                  </q-badge>

                  <q-btn
                    v-else
                    dense
                    unelevated
                    color="grey-5"
                    text-color="white"
                    label="Set Active"
                    size="sm"
                    class="q-px-sm"
                    @click="setActivePlayer(member.profile)"
                  />
                </div>

                <q-btn
                  dense
                  flat
                  round
                  color="red-6"
                  icon="delete_outline"
                  size="sm"
                  @click="onDeleteSelectedGame(member, selGame)"
                >
                  <q-tooltip>Delete Game</q-tooltip>
                </q-btn>
              </div>
            </div>
          </q-card-section>

          <q-separator size="2px" color="grey-4" />

          <!-- Game Settings Section -->
          <q-card-section class="q-pa-none">
            <q-expansion-item
              default-closed
              icon="tune"
              label="Game Settings"
              :header-class="['text-weight-bold bg-grey-1 q-py-md', 'text-grey-8']"
              expand-icon-class="text-primary"
            >
              <q-separator />
              <q-card-section class="bg-white q-pa-md">
                <GameSettingsDisplay
                  v-if="selGame"
                  :selectedOptions="selGame.selected_options"
                />
                <div v-else class="text-grey-5 text-center q-py-lg text-body1">
                  No game settings available
                </div>
              </q-card-section>

              <q-card-actions align="right" class="bg-grey-1 q-px-md q-py-sm">
                <KennerButton
                  flat
                  v-if="selGame"
                  label="Edit Settings"
                  icon="edit"
                  color="secondary"
                  size="md"
                  @click="() => (editingGame = { member, selGame })"
                />
              </q-card-actions>
            </q-expansion-item>
          </q-card-section>

          <q-separator size="2px" color="grey-4" />

          <!-- Match Result Section -->
          <q-card-section class="q-pa-none">
            <q-expansion-item
              :default-opened="false"
              icon="emoji_events"
              label="Match Result"
              :header-class="[
                'text-weight-bold bg-grey-1 q-py-md',
                hasResult(member, selGame) ? 'text-grey-8' : 'text-grey-5',
              ]"
              expand-icon-class="text-primary"
            >
              <q-separator />

              <q-card-section class="bg-white q-pa-md" v-if="hasResult(member, selGame)">
                <MatchResult
                  :displayGameName="false"
                  :selectedGame="selGame"
                  :matchResults="matchResultsBySelectedGameId"
                />
              </q-card-section>

              <q-card-section class="bg-white q-py-lg" v-else>
                <div class="text-grey-5 text-center text-body1">
                  <q-icon name="primary_outline" size="sm" class="q-mr-sm" />
                  No results posted yet
                </div>
              </q-card-section>

              <q-card-actions align="right" class="bg-grey-1 q-px-md q-py-sm">
                <KennerButton
                  v-if="hasResult(member, selGame)"
                  flat
                  label="Edit Result"
                  icon="edit_note"
                  color="secondary"
                  size="md"
                  @click="() => (editResultForSelGameId = selGame.id)"
                />
                <KennerButton
                  v-else
                  flat
                  label="Post Result"
                  icon="post_add"
                  color="primary"
                  size="md"
                  @click="() => (postResultForSelGame = selGame)"
                />
              </q-card-actions>
            </q-expansion-item>
          </q-card-section>
        </q-card>
      </div>

      <!-- Optional card if member has no selected games -->
      <div
        v-if="!member.selected_games || member.selected_games.length === 0"
        :key="`${member.id}-no-games`"
        class="col-12 col-md-6"
      >
        <q-card
          flat
          bordered
          class="fit rounded-borders overflow-hidden"
          v-if="showPlayerGrid"
        >
          <q-card-section class="q-pa-lg bg-grey-3">
            <div class="row items-center justify-between">
              <div class="col">
                <div class="text-h6 text-weight-bold text-grey-9">
                  <q-icon name="sports_esports" size="sm" class="q-mr-sm" />
                  No Game Selected
                </div>
              </div>
              <div class="col-auto row items-center q-gutter-md">
                <q-badge color="dark" text-color="white">
                  <q-icon name="person" size="xs" class="q-mr-xs" />
                  <span class="text-weight-medium">{{ member.profile_name }}</span>
                </q-badge>
                <KennerButton
                  flat
                  label="Select Game"
                  icon="add"
                  color="primary"
                  size="md"
                  @click="() => (selectingGameMember = member)"
                />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </template>

    <!-- Form to edit a member's selected game -->
    <FormLayout v-if="editingGame" @onClose="closeForm">
      <template #head>
        Edit Game
        <span class="text-primary">{{ editingGame.selGame?.game_name }}</span>
        for
        <span class="text-primary">{{ editingGame.member?.profile_name || '' }}</span>
      </template>
      <GameSettingsEditor
        :leagueId="league.id"
        :profileId="editingGame.member.profile"
        :gameId="editingGame.selGame.game"
        :selectedGameId="editingGame.selGame.id"
        @onSuccess="onSuccessfulGameEdit"
      />
    </FormLayout>

    <!-- Form to select a game -->
    <FormLayout v-if="selectingGameMember" @onClose="closeForm">
      <template #head>
        Select a game for
        <span class="text-primary">{{ selectingGameMember.profile_name }}</span>
      </template>
      <GameSelectionView
        manageOnly
        :leagueId="league.id"
        :profileId="selectingGameMember.profile"
        @onSuccess="onSuccessfulGameSubmit"
      />
    </FormLayout>

    <!-- Form to post match results -->
    <FormLayout v-if="postResultForSelGame" @onClose="closeForm">
      <template #head>
        Post Match Results for
        <span class="text-primary">{{ postResultForSelGame.game_name }}</span>
      </template>
      <MatchResultForm
        :selectedGameId="postResultForSelGame.id"
        :leagueId="league.id"
        @submitted="
          () => {
            closeForm();
            load();
          }
        "
      />
    </FormLayout>

    <!-- Form to edit match results (placeholder like before) -->
    <div v-if="editResultForSelGameId"></div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';
import { fetchLeagueDetails } from 'src/services/leagueService';
import { fetchSeason } from 'src/services/seasonService';
import ErrorDisplay from 'components/base/ErrorDisplay.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import KennerButton from 'components/base/KennerButton.vue';
import FormLayout from 'components/league/manager/FormLayout.vue';
import GameSelectionView from 'components/game/selectedGame/GameSelectionView.vue';
import GameSettingsEditor from 'components/game/selectedGame/GameSettingsEditor.vue';
import GameSettingsDisplay from 'components/game/selectedGame/GameSettingsDisplay.vue';
import MatchResultForm from 'components/league/MatchResultForm.vue';
import MatchResult from 'components/league/MatchResult.vue';
import { useDialog } from 'src/composables/dialog';
import type { TSeason } from 'src/types';

type SelectedGame = {
  id: number;
  game: number;
  game_name: string;
  selected_options: any[];
};

type Member = any;

const route = useRoute();
const $q = useQuasar();
const { setDialog } = useDialog();

const league = ref<any | null>(null);
const season = ref<TSeason | null>(null);

/**
 * Results are keyed by selectedGameId (NOT by member).
 * This allows any member to have many games and many results without overwriting.
 */
const matchResultsBySelectedGameId = ref<Record<number, any[]>>({});

const loading = ref(false);
const error = ref<string | null>(null);

const editingGame = ref<{ member: Member; selGame: SelectedGame } | null>(null);
const selectingGameMember = ref<Member | null>(null);
const postResultForSelGame = ref<SelectedGame | null>(null);
const editResultForSelGameId = ref<number | null>(null);

const showPlayerGrid = computed(
  () =>
    !selectingGameMember.value &&
    !editingGame.value &&
    !postResultForSelGame.value &&
    !editResultForSelGameId.value
);

async function load() {
  loading.value = true;
  error.value = null;

  try {
    const leagueId = Number(route.params.id);
    league.value = await fetchLeagueDetails(leagueId);
    if (!league.value) throw new Error('Failed to load league data.');

    season.value = await fetchSeason(league.value.season);
    await fetchMatchResults();
  } catch (e: any) {
    error.value = e?.message || 'Failed to load league/season data.';
  } finally {
    loading.value = false;
  }
}

async function fetchMatchResults() {
  matchResultsBySelectedGameId.value = {};

  const tasks: Promise<void>[] = [];

  for (const member of league.value?.members || []) {
    for (const selGame of member.selected_games || []) {
      tasks.push(fetchMatchResult(selGame));
    }
  }

  await Promise.all(tasks);
}

async function fetchMatchResult(selGame: SelectedGame) {
  try {
    const { data } = await api.get(
      `result/results/?season=${season.value?.id}&league=${league.value?.id}&selected_game=${selGame.id}`
    );

    matchResultsBySelectedGameId.value = {
      ...matchResultsBySelectedGameId.value,
      [selGame.id]: Array.isArray(data) ? data : [],
    };
  } catch (e: any) {
    // ok if none exist
    matchResultsBySelectedGameId.value = {
      ...matchResultsBySelectedGameId.value,
      [selGame.id]: [],
    };
    console.log('No results uploaded', e);
  }
}

async function setActivePlayer(profileId: number) {
  try {
    const { data } = await api.post(
      `league/leagues/${league.value.id}/set-active-player/`,
      { profile_id: profileId },
      { headers: { 'Content-Type': 'application/json' } }
    );
    league.value.active_player = data.profile;
  } catch (e) {
    $q.notify({
      type: 'negative',
      message: 'Failed to set active player',
    });
  }
}

function hasResult(_member: Member, selGame: SelectedGame) {
  const results = matchResultsBySelectedGameId.value[selGame.id];
  return Array.isArray(results) && results.length > 0;
}

function closeForm() {
  selectingGameMember.value = null;
  editingGame.value = null;
  postResultForSelGame.value = null;
  editResultForSelGameId.value = null;
}

async function onDeleteSelectedGame(member: Member, selGame: SelectedGame) {
  setDialog(
    'Delete Game Selection',
    `This will permanently delete the game "${selGame.game_name}" and all associated results. This action cannot be undone.`,
    'negative',
    async () => {
      try {
        await api.delete(`game/selected-games/${selGame.id}/`);
        await load();
        $q.notify({
          type: 'positive',
          message: 'Game selection deleted successfully',
        });
      } catch (err) {
        console.error('Delete failed', err);
        $q.notify({
          type: 'negative',
          message: 'Failed to delete game selection',
        });
      }
    },
    undefined,
    'Delete'
  );
}

function onSuccessfulGameSubmit() {
  selectingGameMember.value = null;
  void load();
}

function onSuccessfulGameEdit() {
  editingGame.value = null;
  void load();
}

onMounted(load);
</script>

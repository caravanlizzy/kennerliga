<template>
  <!-- Header -->
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
      >L {{ league.level }}
      </q-chip>
    </div>
    <div class="col-auto">
      <q-btn flat icon="refresh" round color="teal-7" size="md" @click="load">
        <q-tooltip>Refresh</q-tooltip>
      </q-btn>
    </div>
  </div>
  <!-- Loading -->
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
  <!-- Members grid -->
  <div v-else class="row q-col-gutter-lg">
    <div
      v-for="member in league?.members"
      :key="member.id"
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
                {{
                  member.selected_game
                    ? member.selected_game.game_name
                    : 'No Game Selected'
                }}
              </div>
            </div>
            <div class="col-auto row items-center q-gutter-md">
              <q-badge color="dark" text-color="white" class="">
                <q-icon name="person" size="xs" class="q-mr-xs" />
                <span class="text-weight-medium">{{
                  member.profile_name
                }}</span>
              </q-badge>
              <div
                v-if="
                  ['PICKING', 'REPICKING', 'BANNING'].includes(league.status) &&
                  season.status === 'RUNNING'
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
                v-if="member.selected_game"
                dense
                flat
                round
                color="red-6"
                icon="delete_outline"
                size="sm"
                @click="onDeleteSelectedGame(member)"
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
            header-class="text-weight-bold text-grey-8 bg-grey-1 q-py-md"
            expand-icon-class="text-teal-7"
          >
            <q-separator />
            <q-card-section class="bg-white q-pa-md">
              <GameSettingsDisplay
                v-if="member.selected_game"
                :selectedOptions="member.selected_game.selected_options"
              />
              <div v-else class="text-grey-5 text-center q-py-lg text-body1">
                No game settings available
              </div>
            </q-card-section>
            <q-card-actions align="right" class="bg-grey-1 q-px-md q-py-sm">
              <KennerButton
                flat
                v-if="member.selected_game"
                label="Edit Settings"
                icon="edit"
                color="teal-7"
                size="md"
                @click="() => (editingGameMember = member)"
              />
              <KennerButton
                v-else
                flat
                label="Select Game"
                icon="add"
                color="teal-7"
                size="md"
                @click="() => (selectingGameMember = member)"
              />
            </q-card-actions>
          </q-expansion-item>
        </q-card-section>
        <q-separator size="2px" color="grey-4" />
        <!-- Match Result Section -->
        <q-card-section class="q-pa-none">
          <q-expansion-item
            :default-opened="hasResult(member)"
            icon="emoji_events"
            label="Match Result"
            header-class="text-weight-bold text-grey-8 bg-grey-1 q-py-md"
            expand-icon-class="text-teal-7"
          >
            <q-separator />
            <q-card-section class="bg-white q-pa-md" v-if="hasResult(member)">
              <MatchResult
                :displayGameName="false"
                :selectedGame="member.selected_game"
                :matchResults="matchResults"
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
                v-if="hasResult(member)"
                flat
                label="Edit Result"
                icon="edit_note"
                color="amber-9"
                size="md"
                @click="
                  () => (editResultForSelGameId = member.selected_game.id)
                "
              />
              <KennerButton
                v-else-if="member.selected_game"
                flat
                label="Post Result"
                icon="post_add"
                color="teal-7"
                size="md"
                @click="() => (postResultForSelGame = member.selected_game)"
              />
            </q-card-actions>
          </q-expansion-item>
        </q-card-section>
      </q-card>
    </div>
    <!--    Form to edit a members game selection-->
    <FormLayout v-if="editingGameMember" @onClose="closeForm">
      <template #head>
        Edit Game
        <span class="text-teal-7">{{
          editingGameMember.selected_game?.game_name
        }}</span>
        for
        <span class="text-teal-7">{{
          editingGameMember.profile_name.replace('_profile', '')
        }}</span>
      </template>
      <GameSettingsEditor
        :leagueId="league.id"
        :profileId="editingGameMember.profile"
        :gameId="editingGameMember.selected_game.game"
        :selectedGameId="editingGameMember.selected_game.id"
        @onSuccess="onSuccessfulGameEdit"
      />
    </FormLayout>
    <!-- Form to select a game -->
    <FormLayout v-if="selectingGameMember" @onClose="closeForm">
      <template #head>
        Select a game for
        <span class="text-teal-7">{{ selectingGameMember.profile_name }}</span>
      </template>
      <GameSelector
        manageOnly
        :leagueId="league.id"
        :profileId="selectingGameMember!.profile"
        @onSuccess="onSuccessfulGameSubmit"
      />
    </FormLayout>
    <!--      Form to post match results-->
    <FormLayout @onClose="closeForm" v-if="postResultForSelGame">
      <template #head>
        Post Match Results for
        <span class="text-teal-7"> {{ postResultForSelGame.game_name }} </span>
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
    <!--      Form to edit match results-->
    <div v-if="editResultForSelGameId"></div>
  </div>
</template>

<script setup lang="ts">
import { fetchLeagueDetails } from 'src/services/leagueService';
import { fetchSeason } from 'src/services/seasonService';
import ErrorDisplay from 'components/base/ErrorDisplay.vue';
import { computed, onMounted, ref } from 'vue';
import { TLeagueMember, TSeason } from 'src/types';
import { useRoute } from 'vue-router';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { api } from 'boot/axios';
import { useQuasar } from 'quasar';
import FormLayout from 'components/league/manager/FormLayout.vue';
import GameSelector from 'components/game/selectedGame/GameSelector.vue';
import GameSettingsEditor from 'components/game/selectedGame/GameSettingsEditor.vue';
import MatchResultForm from 'components/league/MatchResultForm.vue';
import MatchResult from 'components/league/MatchResult.vue';
import GameSettingsDisplay from 'components/game/selectedGame/GameSettingsDisplay.vue';
import { useDialog } from 'src/composables/dialog';

const route = useRoute();
const $q = useQuasar();
const { setDialog } = useDialog();

// league and season data
const league = ref<any | null>(null);
const season = ref<TSeason | null>(null);
const matchResults = ref({});

const loading = ref(false);
const error = ref<string | null>(null);

// vars to control which form is shown if any
const editingGameMember = ref<any | null>(null);
const selectingGameMember = ref<TLeagueMember | null>(null);
const postResultForSelGame = ref(null);
const editResultForSelGameId = ref(null);
const showPlayerGrid = computed(
  () =>
    !selectingGameMember.value &&
    !editingGameMember.value &&
    !postResultForSelGame.value &&
    !editResultForSelGameId.value
);

/**
 * Loads league and season data based on the route parameters.
 * Sets the loading state, handles errors, and fetches required data asynchronously.
 *
 * @return {Promise<void>} A promise that resolves when the league and season data are loaded.
 */
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
  for (const member of league.value?.members || []) {
    if (member.selected_game) {
      await fetchMatchResult(member);
    }
  }
}

async function fetchMatchResult(member: TLeagueMember) {
  try {
    const { data } = await api.get(
      `result/results/?season=${season.value?.id}&league=${league.value?.id}&selected_game=${member.selected_game.id}`
    );
    matchResults.value[member.profile] = data;
  } catch (e: any) {
    console.log('No results uploaded', e);
  }
}

async function setActivePlayer(profileId) {
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

function hasResult(member: TLeagueMember) {
  const selGame = member.selected_game;
  if (!selGame) return false;

  const results = matchResults.value[member.profile];
  if (!results || results.length === 0) return false;

  return results.some((mr) => mr.selected_game === selGame.id);
}

function closeForm() {
  selectingGameMember.value = null;
  editingGameMember.value = null;
  postResultForSelGame.value = null;
  editResultForSelGameId.value = null;
}

// onSubmit function handlers

// Delete Game Selection
async function onDeleteSelectedGame(member: any) {
  setDialog(
    'Delete Game Selection',
    `This will permanently delete the game "${member.selected_game.game_name}" and all associated results. This action cannot be undone.`,
    'negative',
    async () => {
      try {
        await api.delete(`game/selected-games/${member.selected_game.id}/`);
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

// Create Game Selection
function onSuccessfulGameSubmit() {
  selectingGameMember.value = null;
  void load();
}

// Edit Game Selection
function onSuccessfulGameEdit() {
  editingGameMember.value = null;
  void load();
}

onMounted(load);
</script>

<template>
  <!-- Header -->
  <div v-if="!loading" class="row items-center q-mb-lg">
    <div class="col-grow">
      <div class="text-h5 text-weight-bold">
        Manage {{ loading ? '' : 'L' + league?.level }}
        <q-badge class="q-ml-sm" outline>League</q-badge>
      </div>
      <div class="text-subtitle2 text-grey-7">
        Season: <q-chip dense square>{{ loading ? '' : season?.name }} - {{season?.status}}</q-chip>
      </div>
    </div>
    <div class="col-auto">
      <q-btn flat icon="refresh" round @click="load" />
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
    class="q-pa-xl flex items-center justify-center"
  >
    <div class="column items-center">
      <q-icon name="group_off" size="48px" class="q-mb-sm" />
      <div class="text-subtitle1">No members yet</div>
      <div class="text-caption text-grey-7 q-mt-xs">
        Add members to start selecting games.
      </div>
    </div>
  </q-card>

  <!-- Members grid -->
  <div v-else class="row q-col-gutter-md">
    <div
      v-for="member in league?.members"
      :key="member.id"
      class="col-12 col-md-6"
    >
      <q-card flat bordered class="fit" v-if="showPlayerGrid">
        <!-- Player Header Section -->
        <q-card-section class="bg-primary text-white q-pa-md">
          <div class="row items-center justify-between">
            <div class="col">
              <div class="text-h6 text-weight-medium">
                <q-icon name="person" size="sm" class="q-mr-xs" />
                {{ member.profile_name }}
              </div>
            </div>
            <div class="col-auto" v-if="['PICKING', 'REPICKING', 'BANNING'].includes(league.status) && season.status === 'RUNNING'">
              <q-badge
                v-if="member.profile === league.active_player"
                color="positive"
                class="q-py-xs q-px-sm"
              >
                <q-icon size="xs" name="star" class="q-mr-xs" /> Active Player
              </q-badge>
              <q-btn
                v-else
                dense
                outline
                color="white"
                label="Set Active"
                size="sm"
                @click="setActivePlayer(member.profile)"
              />
            </div>
          </div>
          <div class="q-mt-sm">
            <div v-if="member.selected_game" class="text-subtitle1 text-weight-medium">
              <q-icon name="sports_esports" size="sm" class="q-mr-xs" />
              {{ member.selected_game.game_name }}
            </div>
            <q-badge
              v-else
              color="grey-4"
              text-color="dark"
              class="text-uppercase"
            >
              No game selected
            </q-badge>
          </div>
        </q-card-section>

        <q-separator />

        <!-- Match Result Section -->
        <div v-if="hasResult(member)" class="bg-grey-2">
          <q-card-section class="q-pb-none">
            <div class="text-subtitle2 text-weight-bold text-grey-8 q-mb-sm">
              <q-icon name="emoji_events" size="sm" class="q-mr-xs" />
              Match Result
            </div>
            <MatchResult
              :displayGameName="false"
              :selectedGame="member.selected_game"
            />
          </q-card-section>
          <q-card-actions align="right" class="q-px-md q-pb-md">
            <KennerButton
              outline
              label="Edit Result"
              icon="edit_note"
              color="accent"
              size="sm"
              @click="() => (editResultForSelGameId = member.selected_game.id)"
            />
          </q-card-actions>
          <q-separator />
        </div>

        <!-- Game Settings Section -->
        <q-card-section class="q-pa-none">
          <q-expansion-item
            dense
            default-opened
            icon="settings"
            label="Game Settings"
            header-class="text-weight-bold text-grey-8 bg-grey-1"
            expand-icon="expand_more"
          >
            <q-card-section class="bg-grey-1 q-pt-sm">
              <GameSettingsDisplay
                v-if="member.selected_game"
                :selectedOptions="member.selected_game.selected_options"
              />
              <div v-else class="text-grey-6 text-center q-py-md">
                No game settings available
              </div>
            </q-card-section>
          </q-expansion-item>
        </q-card-section>

        <q-separator />

        <!-- Actions Section -->
        <q-card-actions align="right" class="bg-grey-3 q-pa-md">
          <KennerButton
            outline
            v-if="member.selected_game"
            label="Edit Settings"
            icon="edit"
            color="accent"
            @click="() => (editingGameMember = member)"
          />
          <KennerButton
            v-else
            outline
            label="Select Game"
            icon="add"
            color="primary"
            @click="() => (selectingGameMember = member)"
          />
          <KennerButton
            outline
            v-if="member.selected_game"
            label="Delete Game"
            icon="delete"
            color="negative"
            @click="onDeleteSelectedGame(member)"
          />
          <KennerButton
            v-if="member.selected_game && !hasResult(member)"
            outline
            label="Post Result"
            icon="post_add"
            color="primary"
            @click="() => (postResultForSelGame = member.selected_game)"
          />
        </q-card-actions>
      </q-card>
    </div>
    <!--    Form to edit a members game selection-->
    <FormLayout v-if="editingGameMember" @onClose="closeForm">
      <template #head>
        Edit Game
        <span class="text-primary">{{
          editingGameMember.selected_game?.game_name
        }}</span>
        for
        <span class="text-primary">{{
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
        <span class="text-primary">{{ selectingGameMember.profile_name }}</span>
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
        <span class="text-primary"> {{ postResultForSelGame.game_name }} </span>
      </template>
      <MatchResultForm
        :selectedGameId="postResultForSelGame.id"
        :leagueId="league.id"
        @submitted="closeForm"
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

const route = useRoute();
const $q = useQuasar();

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
  selectingGameMember.value = null;
  try {
    await api.delete(`game/selected-games/${member.selected_game.id}/`);
    await load();
  } catch (err) {
    console.error('Delete failed', err);
  }
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

<template>
  <q-page class="q-pa-md">
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
        <q-btn
          flat
          icon="refresh"
          round
          color="secondary"
          size="md"
          @click="load"
        >
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

    <!-- Members Grid -->
    <div v-else class="row q-col-gutter-xl">
      <template v-for="member in league?.members" :key="member.id">
        <div class="col-12">
          <!-- Member Group Header -->
          <div class="row items-center q-mb-sm q-gutter-sm">
            <q-avatar color="primary" text-color="white" size="md">
              {{ member.profile_name.charAt(0).toUpperCase() }}
            </q-avatar>
            <div class="text-h5 text-weight-bold text-grey-9">
              {{ member.profile_name }}
            </div>
            <!-- Banned Game Display -->
            <q-chip
              v-if="member.my_banned_game"
              outline
              square
              color="red-7"
              text-color="red-7"
              icon="block"
              class="q-ml-sm"
            >
              Banned: {{ member.my_banned_game.game_name }}
              <q-btn
                flat
                round
                dense
                size="xs"
                icon="close"
                class="q-ml-xs"
                @click="onDeleteBannedGame(member.my_banned_game.id)"
              >
                <q-tooltip>Remove Ban</q-tooltip>
              </q-btn>
            </q-chip>
            <q-space />
            <div
              v-if="
                ['PICKING', 'REPICKING', 'BANNING'].includes(league.status) &&
                season?.status === 'RUNNING'
              "
            >
              <q-badge
                v-if="member.id === league.active_player"
                color="positive"
                text-color="white"
                class="q-py-xs q-px-sm"
              >
                <q-icon size="xs" name="star" class="q-mr-xs" />
                <span class="text-weight-bold">Active Player</span>
              </q-badge>
            </div>
          </div>

          <!-- Quick Actions Bar -->
          <div class="row q-gutter-sm q-mb-md">
            <KennerButton
              v-if="(member.selected_games?.length || 0) < 2"
              outline
              dense
              color="primary"
              icon="add_circle"
              label="Add Game"
              class="q-px-sm"
              @click="() => (selectingGameMember = member)"
            />
            <KennerButton
              v-if="!member.my_banned_game"
              outline
              dense
              color="red-7"
              icon="block"
              label="Ban Game"
              class="q-px-sm"
              @click="() => (banningGameMember = member)"
            />
            <KennerButton
              v-if="
                member.id !== league.active_player &&
                ['PICKING', 'REPICKING', 'BANNING'].includes(league.status) &&
                season?.status === 'RUNNING'
              "
              outline
              dense
              color="secondary"
              icon="person_outline"
              label="Set Active"
              class="q-px-sm"
              @click="setActivePlayer(member.profile)"
            />
          </div>

          <div class="row q-col-gutter-lg">
            <!-- Card per selected game -->
            <div
              v-for="selGame in member.selected_games || []"
              :key="`${member.id}-${selGame.id}`"
              class="col-12 col-md-4"
            >
              <q-card flat bordered class="fit rounded-borders overflow-hidden">
                <!-- Header Section -->
                <q-card-section class="q-pa-md bg-grey-2">
                  <div class="row items-center justify-between">
                    <div class="col">
                      <div class="text-subtitle1 text-weight-bold text-grey-9">
                        <q-icon
                          name="sports_esports"
                          size="xs"
                          class="q-mr-xs"
                        />
                        {{ selGame?.game_name || 'No Game Selected' }}
                      </div>
                    </div>
                    <div class="col-auto">
                      <div class="row items-center q-gutter-xs">
                        <q-btn
                          flat
                          dense
                          round
                          color="secondary"
                          icon="edit"
                          size="sm"
                          @click="() => (editingGame = { member, selGame })"
                        >
                          <q-tooltip>Edit Settings</q-tooltip>
                        </q-btn>
                        <q-btn
                          flat
                          dense
                          round
                          :color="
                            hasResult(member, selGame) ? 'secondary' : 'primary'
                          "
                          :icon="
                            hasResult(member, selGame)
                              ? 'edit_note'
                              : 'post_add'
                          "
                          size="sm"
                          @click="
                            () =>
                              hasResult(member, selGame)
                                ? (editResultForSelGameId = selGame.id)
                                : (postResultForSelGame = selGame)
                          "
                        >
                          <q-tooltip>{{
                            hasResult(member, selGame)
                              ? 'Edit Result'
                              : 'Post Result'
                          }}</q-tooltip>
                        </q-btn>
                        <q-btn
                          flat
                          dense
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
                  </div>
                </q-card-section>

                <!-- Game Content Sections (Expandables) -->
                <q-card-section class="q-pa-none">
                  <q-expansion-item
                    dense
                    icon="tune"
                    label="Settings"
                    header-class="text-weight-bold text-grey-7 bg-grey-1"
                  >
                    <q-card-section class="bg-white q-pa-md">
                      <GameSettingsDisplay
                        :selectedOptions="selGame.selected_options"
                      />
                    </q-card-section>
                  </q-expansion-item>
                  <q-separator />
                  <q-expansion-item
                    dense
                    icon="emoji_events"
                    label="Match Result"
                    header-class="text-weight-bold text-grey-7 bg-grey-1"
                  >
                    <q-card-section class="bg-white q-pa-md">
                      <MatchResult
                        v-if="hasResult(member, selGame)"
                        :displayGameName="false"
                        :selectedGame="selGame"
                        :matchResults="matchResultsBySelectedGameId"
                      />
                      <div v-else class="text-grey-5 text-center q-py-sm">
                        No results posted
                      </div>
                    </q-card-section>
                  </q-expansion-item>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </div>
      </template>

      <!-- Unified Dialog for all Forms -->
      <q-dialog
        :model-value="
          !!(
            editingGame ||
            selectingGameMember ||
            banningGameMember ||
            postResultForSelGame ||
            editResultForSelGameId
          )
        "
        @update:model-value="closeForm"
        persistent
      >
        <div style="min-width: 450px; max-width: 90vw">
          <FormLayout v-if="editingGame" @onClose="closeForm">
            <template #head>
              Edit Game
              <span class="text-primary">{{
                editingGame.selGame?.game_name
              }}</span>
              for
              <span class="text-primary">{{
                editingGame.member?.profile_name
              }}</span>
            </template>
            <GameSettingsEditor
              :leagueId="league.id"
              :profileId="editingGame.member.profile"
              :gameId="editingGame.selGame.game"
              :selectedGameId="editingGame.selGame.id"
              @onSuccess="onSuccessfulGameEdit"
            />
          </FormLayout>

          <FormLayout v-if="selectingGameMember" @onClose="closeForm">
            <template #head>
              Select Game for
              <span class="text-primary">{{
                selectingGameMember.profile_name
              }}</span>
            </template>
            <GameSelectionView
              manageOnly
              :leagueId="league.id"
              :profileId="selectingGameMember.profile"
              @onSuccess="onSuccessfulGameSubmit"
            />
          </FormLayout>

          <FormLayout v-if="banningGameMember" @onClose="closeForm">
            <template #head>
              Ban Game for
              <span class="text-primary">{{
                banningGameMember.profile_name
              }}</span>
            </template>
            <BanGameForm
              :league="league"
              :member="banningGameMember"
              @onSuccess="onSuccessfulGameSubmit"
            />
          </FormLayout>

          <FormLayout v-if="postResultForSelGame" @onClose="closeForm">
            <template #head>
              Post Result for
              <span class="text-primary">{{
                postResultForSelGame.game_name
              }}</span>
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
        </div>
      </q-dialog>

      <div v-if="editResultForSelGameId"></div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';
import { fetchLeagueDetails } from 'src/services/leagueService';
import { fetchSeason } from 'src/services/seasonService';
import ErrorDisplay from 'components/base/ErrorDisplay.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import FormLayout from 'components/league/manager/FormLayout.vue';
import GameSelectionView from 'components/game/selectedGame/GameSelectionView.vue';
import GameSettingsEditor from 'components/game/selectedGame/GameSettingsEditor.vue';
import GameSettingsDisplay from 'components/game/selectedGame/GameSettingsDisplay.vue';
import MatchResultForm from 'components/league/MatchResultForm.vue';
import MatchResult from 'components/league/MatchResult.vue';
import { useDialog } from 'src/composables/dialog';
import type { TSeason } from 'src/types';
import BanGameForm from 'components/game/selectedGame/BanGameForm.vue';
import KennerButton from 'components/base/KennerButton.vue';

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
const matchResultsBySelectedGameId = ref<Record<number, any[]>>({});

const loading = ref(false);
const error = ref<string | null>(null);

const editingGame = ref<{ member: Member; selGame: SelectedGame } | null>(null);
const selectingGameMember = ref<Member | null>(null);
const banningGameMember = ref<Member | null>(null);
const postResultForSelGame = ref<SelectedGame | null>(null);
const editResultForSelGameId = ref<number | null>(null);

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
    matchResultsBySelectedGameId.value = {
      ...matchResultsBySelectedGameId.value,
      [selGame.id]: [],
    };
  }
}

async function setActivePlayer(profileId: number) {
  try {
    const { data } = await api.post(
      `league/leagues/${league.value.id}/set-active-player/`,
      { profile_id: profileId }
    );
    league.value.active_player = data.participant_id;
  } catch (e) {
    $q.notify({ type: 'negative', message: 'Failed to set active player' });
  }
}

function hasResult(_member: Member, selGame: SelectedGame) {
  const results = matchResultsBySelectedGameId.value[selGame.id];
  return Array.isArray(results) && results.length > 0;
}

function closeForm() {
  selectingGameMember.value = null;
  banningGameMember.value = null;
  editingGame.value = null;
  postResultForSelGame.value = null;
  editResultForSelGameId.value = null;
}

async function onDeleteSelectedGame(member: Member, selGame: SelectedGame) {
  setDialog(
    'Delete Game Selection',
    `Permanently delete "${selGame.game_name}" and all results?`,
    'warning',
    async () => {
      try {
        await api.delete(`game/selected-games/${selGame.id}/`);
        await load();
        $q.notify({ type: 'positive', message: 'Selection deleted' });
      } catch (err) {
        $q.notify({ type: 'negative', message: 'Failed to delete selection' });
      }
    },
    undefined,
    'Delete'
  );
}

function onSuccessfulGameSubmit() {
  closeForm();
  void load();
}

function onSuccessfulGameEdit() {
  editingGame.value = null;
  void load();
}

onMounted(load);
</script>

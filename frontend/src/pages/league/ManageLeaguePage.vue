<template>
  <q-page class="q-pa-md">
    <!-- Header -->
    <LeagueHeader
      v-if="!loading && league"
      :league="league"
      :season="season"
      @refresh="load"
    />

    <!-- Loading / Error -->
    <LoadingSpinner v-if="loading" />
    <ErrorDisplay v-else-if="error" :error="error" class="q-mb-md" />

    <!-- Empty state -->
    <EmptyMembersState
      v-else-if="!league?.members || league.members.length === 0"
    />

    <!-- Members Grid -->
    <div v-else class="row q-col-gutter-xl">
      <MemberGameCard
        v-for="member in league?.members"
        :key="member.id"
        :member="member"
        :league="league"
        :season="season"
        :matchResultsBySelectedGameId="matchResultsBySelectedGameId"
        @add-game="m => (selectingGameMember = m)"
        @ban-game="m => (banningGameMember = m)"
        @set-active="profileId => setActivePlayer(profileId)"
        @edit-game="data => (editingGame = data)"
        @edit-result="id => (editResultForSelGameId = id)"
        @post-result="selGame => (postResultForSelGame = selGame)"
        @delete-game="data => onDeleteSelectedGame(data.member, data.selGame)"
      />

      <!-- Unified Dialog for all Forms -->
      <ManagerFormsDialog
        v-if="league"
        :league="league"
        :editingGame="editingGame"
        :selectingGameMember="selectingGameMember"
        :banningGameMember="banningGameMember"
        :postResultForSelGame="postResultForSelGame"
        :editResultForSelGameId="editResultForSelGameId"
        @close="closeForm"
        @success-submit="onSuccessfulGameSubmit"
        @success-edit="onSuccessfulGameEdit"
        @success-result="
          () => {
            closeForm();
            load();
          }
        "
      />

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
import LeagueHeader from 'components/league/manager/LeagueHeader.vue';
import EmptyMembersState from 'components/league/manager/EmptyMembersState.vue';
import MemberGameCard from 'components/league/manager/MemberGameCard.vue';
import ManagerFormsDialog from 'components/league/manager/ManagerFormsDialog.vue';
import { useDialog } from 'src/composables/dialog';
import type { TSeason, TLeague, TLeagueMember, TSelectedGameDto, TMatchResult } from 'src/types';

const route = useRoute();
const $q = useQuasar();
const { setDialog } = useDialog();

const league = ref<TLeague | null>(null);
const season = ref<TSeason | null>(null);
const matchResultsBySelectedGameId = ref<Record<number, TMatchResult[]>>({});

const loading = ref(false);
const error = ref<string | null>(null);

const editingGame = ref<{ member: TLeagueMember; selGame: TSelectedGameDto } | null>(null);
const selectingGameMember = ref<TLeagueMember | null>(null);
const banningGameMember = ref<TLeagueMember | null>(null);
const postResultForSelGame = ref<TSelectedGameDto | null>(null);
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

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
    <div class="flex justify-center q-my-xl" v-if="loading">
      <LoadingSpinner />
    </div>
    <ErrorDisplay v-else-if="error" :error="error" class="q-mb-md" />

    <!-- Empty state -->
    <EmptyMembersState
      v-else-if="!loading && (!league?.members || league.members.length === 0)"
    />

    <!-- Members Grid -->
    <div v-else-if="!loading && league" class="row q-col-gutter-xl">
      <MemberGameCard
        v-for="member in league?.members"
        :key="member.id"
        :member="member"
        :league="league"
        :season="season"
        :matchResultsBySelectedGameId="matchResultsBySelectedGameId"
        @add-game="m => (activeForm = { type: 'add', member: m })"
        @ban-game="m => (activeForm = { type: 'ban', member: m })"
        @set-active="profileId => setActivePlayer(profileId)"
        @edit-game="data => (activeForm = { type: 'edit', member: data.member, selGame: data.selGame })"
        @post-result="selGame => (activeForm = { type: 'post-result', selGame })"
        @edit-result="selGameId => (activeForm = { type: 'post-result', selGame: findSelGame(selGameId) })"
        @delete-game="data => onDeleteSelectedGame(data.selGame)"
      />

      <!-- Unified Dialog for all Forms -->
      <ManagerFormsDialog
        v-if="league"
        :league="league"
        :activeForm="activeForm"
        @close="activeForm = null"
        @success="onSuccess"
      />
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
import ManagerFormsDialog, { type TActiveForm } from 'components/league/manager/ManagerFormsDialog.vue';
import { useDialog } from 'src/composables/dialog';
import type { TSeasonDto, TLeagueDto, TLeagueMemberDto, TSelectedGameDto, TMatchResult } from 'src/types';

const route = useRoute();
const $q = useQuasar();
const { setDialog } = useDialog();

const league = ref<TLeagueDto | null>(null);
const season = ref<TSeasonDto | null>(null);
const matchResultsBySelectedGameId = ref<Record<number, TMatchResult[]>>({});

const loading = ref(false);
const error = ref<string | null>(null);

const activeForm = ref<TActiveForm | null>(null);

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
  const tasks = (league.value?.members || []).flatMap(member =>
    (member.selected_games || []).map(selGame => fetchMatchResult(selGame))
  );
  await Promise.all(tasks);
}

async function fetchMatchResult(selGame: TSelectedGameDto) {
  try {
    const { data } = await api.get(
      `result/results/?season=${season.value?.id}&league=${league.value?.id}&selected_game=${selGame.id}`
    );
    matchResultsBySelectedGameId.value[selGame.id] = Array.isArray(data) ? data : [];
  } catch (e) {
    matchResultsBySelectedGameId.value[selGame.id] = [];
  }
}

async function setActivePlayer(profileId: number) {
  if (!league.value) return;
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

async function onDeleteSelectedGame(selGame: TSelectedGameDto) {
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

function findSelGame(id: number): TSelectedGameDto | undefined {
  for (const m of league.value?.members || []) {
    const found = m.selected_games?.find(g => g.id === id);
    if (found) return found;
  }
  return undefined;
}

function onSuccess() {
  activeForm.value = null;
  void load();
}

onMounted(load);
</script>

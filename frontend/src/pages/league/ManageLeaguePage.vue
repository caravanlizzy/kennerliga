<template>
  <q-page class="q-pa-md">
    <!-- Header Area -->
    <div class="row items-center justify-between q-mb-md">
      <div class="row items-center q-gutter-x-sm">
        <q-icon name="settings" size="md" color="primary" />
        <div class="text-h4 text-weight-bolder text-dark tracking-tighter">
          Manage League
        </div>
      </div>
      <div class="row items-center q-gutter-x-sm">
        <KennerButton
          v-if="!loading && league"
          flat
          icon="refresh"
          round
          color="primary"
          size="md"
          @click="load"
        >
          <KennerTooltip>Refresh</KennerTooltip>
        </KennerButton>
        <KennerButton
          flat
          icon="close"
          round
          color="grey-7"
          size="md"
          @click="$router.back()"
        >
          <KennerTooltip>Back</KennerTooltip>
        </KennerButton>
      </div>
    </div>

    <!-- Info Section -->
    <div v-if="!loading && league" class="row q-col-gutter-md q-mb-lg">
      <div class="col-12 col-md-6">
        <ContentSection
          title="League Info"
          icon="info"
          color="primary"
          style="margin-top: 0"
          :bordered="false"
        >
          <div class="row q-gutter-sm items-center">
            <q-chip
              square
              color="grey-2"
              text-color="grey-9"
              class="text-weight-bold"
              icon="event"
            >
              {{ season?.name }}
            </q-chip>
            <q-chip
              square
              :color="season?.status === 'RUNNING' ? 'positive' : 'grey-7'"
              text-color="white"
              class="text-weight-bold"
            >
              {{ season?.status }}
            </q-chip>
            <q-chip
              square
              color="secondary"
              text-color="white"
              class="text-weight-bold"
              icon="military_tech"
            >
              Level {{ league?.level }}
            </q-chip>
          </div>
        </ContentSection>
      </div>

      <div class="col-12 col-md-6">
        <ContentSection
          title="Standings"
          icon="leaderboard"
          color="info"
          style="margin-top: 0"
          :bordered="false"
        >
          <LeagueStandings :league-id="league.id" />
        </ContentSection>
      </div>
    </div>

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
    <ContentSection
      v-else-if="!loading && league"
      title="League Members"
      icon="people"
      color="secondary"
      :bordered="false"
    >
      <div class="row q-col-gutter-xl">
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
      </div>
    </ContentSection>

    <!-- Unified Dialog for all Forms -->
    <ManagerFormsDialog
      v-if="league && activeForm"
      :league="league"
      :activeForm="activeForm"
      @close="activeForm = null"
      @success="onSuccess"
    />
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';
import { fetchLeagueDetails } from 'src/services/leagueService';
import { fetchSeason } from 'src/services/seasonService';
import ContentSection from 'components/base/ContentSection.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import KennerButton from 'components/base/KennerButton.vue';
import ErrorDisplay from 'components/base/ErrorDisplay.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import MemberGameCard from 'components/league/manager/MemberGameCard.vue';
import EmptyMembersState from 'components/league/manager/EmptyMembersState.vue';
import LeagueStandings from 'components/league/LeagueStandings.vue';
import ManagerFormsDialog, { type TActiveForm } from 'components/league/manager/ManagerFormsDialog.vue';
import { useDialog } from 'src/composables/dialog';
import type { TSeasonDto, TLeagueDto, TSeasonParticipantDto, TSelectedGameDto, TMatchResult } from 'src/types';

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

    // Results are now included in league.value.members[].selected_games[].results
    // Populate matchResultsBySelectedGameId from the prefetched data
    const newResults: Record<number, TMatchResult[]> = {};
    (league.value.members || []).forEach(member => {
      (member.selected_games || []).forEach(selGame => {
        if (selGame.results) {
          newResults[selGame.id] = selGame.results;
        }
      });
    });
    matchResultsBySelectedGameId.value = newResults;
  } catch (e: any) {
    error.value = e?.message || 'Failed to load league/season data.';
  } finally {
    loading.value = false;
  }
}

async function fetchMatchResult(selGame: TSelectedGameDto) {
  try {
    const { data } = await api.get(
      `result/results/?selected_game=${selGame.id}`
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

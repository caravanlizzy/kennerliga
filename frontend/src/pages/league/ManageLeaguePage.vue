<template>
  <!-- Loading -->
  <LoadingSpinner v-if="loading" />

  <ErrorDisplay v-if="error" :error="error" class="q-mb-md" />

    <!-- Header -->
    <div class="row items-center q-mb-lg">
      <div class="col-grow">
        <div class="text-h5 text-weight-bold">
          Manage L{{ league?.level }}
          <q-badge class="q-ml-sm" outline>League</q-badge>
        </div>
        <div class="text-subtitle2 text-grey-7">
          Season: <q-chip dense square>{{ season?.name }}</q-chip>
        </div>
      </div>
      <div class="col-auto">
        <q-btn flat icon="refresh" round @click="load" />
      </div>
    </div>

    <!-- Empty state -->
    <q-card
      v-if="
        !loading && !error && (!league?.members || league.members.length === 0)
      "
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
          <q-item>
            <q-item-section>
              <q-item-label class="text-weight-medium">
                <q-icon name="person"></q-icon>
                {{ member.username }}
              </q-item-label>
            </q-item-section>
            <q-item-section side>
              <q-badge
                v-if="member.selected_game"
                color="positive"
                outline
                class="text-uppercase"
              >
                {{ member.selected_game.game_name }}
                <q-icon class="q-ml-xs" name="sports_esports" />
              </q-badge>
              <q-badge
                v-else
                color="grey-5"
                text-color="dark"
                outline
                class="text-uppercase"
                >No game yet</q-badge
              >
            </q-item-section>
          </q-item>

          <q-separator />

          <q-card-section>
            <q-expansion-item
              dense
              icon="info"
              label="Game Settings"
              expand-icon="expand_more"
              class="q-mx-sm q-mb-sm"
            >
              <q-card-section class="bg-grey-1">
                <pre v-if="member.selected_game" class="q-ma-none text-body2">{{
                  member.selected_game
                }}</pre>
                <div v-else>No game settings available</div>
              </q-card-section>
            </q-expansion-item>
          </q-card-section>

          <q-separator />

          <q-card-actions align="right">
            <KennerButton
              outline
              v-if="member.selected_game"
              label="Edit Game"
              icon="edit"
              color="primary"
              @click="onEditGame(member)"
            />
            <KennerButton
              v-else
              outline
              label="Select Game"
              icon="add"
              color="primary"
              @click="onSelectGame(member)"
            />
            <KennerButton
              outline
              v-if="member.selected_game"
              label="Delete Game"
              icon="delete"
              color="negative"
              @click="onDeleteSelectedGame(member)"
            >
            </KennerButton>
          </q-card-actions>
        </q-card>
      </div>
      <!--    Edit a members game selection-->
      <ManageLeagueEditGame
        v-if="editingGameMember"
        :editingGameMember="editingGameMember"
        :league="league"
        :onSuccessfulGameEdit="onSuccessfulGameEdit"
        @onClose="close"
      />

      <!-- Form to select a game -->
      <ManageLeagueSelectGame
        v-if="selectingGameMember"
        :selectingGameMember="selectingGameMember"
        :league="league"
        :onSuccessfulGameSubmit="onSuccessfulGameSubmit"
        @onClose="close"
      />
    </div>

<!--  &lt;!&ndash;  <LeagueResultUpload />&ndash;&gt;-->
<!--  <ManageLeagueResults-->
<!--    v-if="!loading && !error"-->
<!--    :selectedGames="selectedGames"-->
<!--  />-->
</template>

<script setup lang="ts">
import ManageLeagueResults from 'components/league/manager/ManageLeagueResults.vue';
import { fetchLeagueDetails } from 'src/services/leagueService';
import { fetchSeason } from 'src/services/seasonService';
import ErrorDisplay from 'components/base/ErrorDisplay.vue';
import { computed, onMounted, ref } from 'vue';
import { TLeague, TLeagueMember, TSeason } from 'src/types';
import { useRoute } from 'vue-router';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import ManageLeagueSelectGame from 'components/league/manager/ManageLeagueSelectGame.vue';
import ManageLeagueEditGame from 'components/league/manager/ManageLeagueEditGame.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { api } from 'boot/axios';

const route = useRoute();

const league = ref<TLeague | null>(null);
const season = ref<TSeason | null>(null);

const loading = ref(false);
const error = ref<string | null>(null);

async function load() {
  loading.value = true;
  error.value = null;
  try {
    const leagueId = Number(route.params.id);
    league.value = await fetchLeagueDetails(leagueId);
    await new Promise((resolve) => setTimeout(resolve, 2000));
    if (!league.value) throw new Error('Failed to load league data.');
    season.value = await fetchSeason(league.value.season);
  } catch (e: any) {
    error.value = e?.message || 'Failed to load league/season data.';
  } finally {
    loading.value = false;
  }
}

const selectedGames = computed(() =>
  league.value?.members.map((m) => m.selected_game)
);

const editingGameMember = ref<any | null>(null);
const selectingGameMember = ref<TLeagueMember | null>(null);
const showPlayerGrid = computed(
  () => !selectingGameMember.value && !editingGameMember.value
);

function close() {
  selectingGameMember.value = null;
  editingGameMember.value = null;
}

// Edit Game
function onEditGame(member: any) {
  editingGameMember.value = member;
}

// Delete Game
async function onDeleteSelectedGame(member: any) {
  selectingGameMember.value = null;
  try {
    await api.delete(`game/selected-games/${member.selected_game.id}/`);
    await load();
  } catch (err) {
    console.error('Delete failed', err);
  }
}

// Select Game
function onSelectGame(member: TLeagueMember) {
  selectingGameMember.value = member;
}

function onSuccessfulGameSubmit() {
  selectingGameMember.value = null;
  load();
}

function onSuccessfulGameEdit() {
  editingGameMember.value = null;
  load();
}

onMounted(load);
</script>

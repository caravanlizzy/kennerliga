<template>
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
      <q-btn flat icon="refresh" round @click="load" :loading="loading" />
    </div>
  </div>

  <!-- Loading -->
  <q-linear-progress v-if="loading" indeterminate class="q-mb-md" />

  <!-- Error -->
  <q-banner
    v-if="error"
    dense
    class="q-mb-md bg-red-1 text-negative"
    rounded
    inline-actions
  >
    <template #avatar>
      <q-icon name="error" />
    </template>
    {{ error }}
    <template #action>
      <q-btn flat color="negative" label="Retry" @click="load" />
    </template>
  </q-banner>

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
      class="col-12 col-sm-6 col-md-4"
    >
      <q-card flat bordered class="fit">
        <q-item>
          <q-item-section avatar>
            <q-avatar rounded>
              <q-icon name="person" />
            </q-avatar>
          </q-item-section>
          <q-item-section>
            <q-item-label class="text-weight-medium">
              {{ member.username }}
            </q-item-label>
          </q-item-section>
          <q-item-section side>
            <q-badge
              v-if="member.selected_game"
              color="positive"
              outline
              class="text-uppercase"
              >Selected</q-badge
            >
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
          <div class="text-caption text-grey-7 q-mb-xs">Selected Game</div>
          <div class="row items-center" style="min-height: 29px">
            <div class="col-auto">
              <q-chip
                v-if="member.selected_game?.game_name"
                icon="sports_esports"
                dense
                square
              >
                {{ member.selected_game.game_name }}
              </q-chip>
              <span v-else class="text-grey-6">No game yet</span>
            </div>
            <div class="col">
              <q-space />
            </div>
          </div>
        </q-card-section>

        <!-- Optional raw data toggle (dev aid) -->
        <q-expansion-item
          dense
          icon="info"
          label="Details"
          expand-icon="expand_more"
          class="q-mx-sm q-mb-sm"
        >
          <q-card-section class="bg-grey-1">
            <pre class="q-ma-none text-body2">{{ member }}</pre>
          </q-card-section>
        </q-expansion-item>

        <q-separator />

        <q-card-actions align="right">
          <q-btn
            outline
            v-if="member.selected_game"
            label="Edit Game"
            icon="edit"
            color="primary"
            @click="onEditGame(member)"
          />
          <q-btn
            v-else
            outline
            label="Select Game"
            icon="add"
            color="primary"
            @click="onSelectGame(member)"
          />
          <q-btn
            outline
            v-if="member.selected_game"
            label="Delete Game"
            icon="delete"
            color="negative"
            @click="onDeleteSelectedGame(member)"
          >
          </q-btn>
        </q-card-actions>
      </q-card>
    </div>

    <!--    Edit a members game selection-->
    <div v-if="currentEditMember !== null">
      <div class="text-h6">
        Edit Game
        {{ currentEditMember.selected_game?.game_name }}
      </div>
      <div
        v-for="option in currentEditMember.selected_game.selected_options"
        :key="option.id"
      >
        {{ option }}
      </div>
      {{ editOptions }}
    </div>

    <!-- Form to select a game -->
    <div
      v-if="selectingGameMember"
      class="q-pa-md q-mt-md bg-grey-1 rounded-borders col-12"
    >
      <div class="row items-center justify-between q-mb-sm">
        <div class="text-h6 text-weight-medium">
          Select a game for
          <span class="text-primary">{{ selectingGameMember.username }}</span>
        </div>
        <q-btn
          dense
          flat
          round
          icon="close"
          color="grey-7"
          @click="selectingGameMember = null"
        />
      </div>

      <q-separator class="q-mb-md" />

      <GameSelector
        manageOnly
        :leagueId="league.id"
        :profileId="selectingGameMember!.profile_id"
        @onSuccess="onSuccessfullGameSelection"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router';
import { onMounted, ref, computed } from 'vue';
import { TLeagueMember, TSeason } from 'src/types';
import { fetchLeagueDetails } from 'src/services/leagueService';
import { fetchSeason } from 'src/services/seasonService';
import { api } from 'boot/axios';
import GameSelector from 'components/game/GameSelector.vue';

const route = useRoute();

const league = ref(null);
const season = ref<TSeason | null>(null);

const loading = ref(false);
const error = ref<string | null>(null);

async function load() {
  loading.value = true;
  error.value = null;
  try {
    const leagueId = Number(route.params.id);
    league.value = await fetchLeagueDetails(leagueId);
    if (!league.value) throw new Error('Failed to load league data.');
    season.value = await fetchSeason(league.value.season);
  } catch (e: any) {
    error.value = e?.message || 'Failed to load league/season data.';
  } finally {
    loading.value = false;
  }
}

// Edit Game
const currentEditMember = ref<any | null>(null);
const editOptions = computed(
  () =>
    currentEditMember.value?.selected_game?.selected_options.map(
      (option: any) =>
        ({}) => ({
          name: option.game_option.name,
          has_choices: option.game_option.has_choices,
          value: option.choice?.value, // fixed the extra dot and added optional chaining
        })
    ) || []
);

function onEditGame(member: any) {
  currentEditMember.value = member;
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
const selectingGameMember = ref<TLeagueMember | null>(null);

function onSelectGame(member: TLeagueMember) {
  selectingGameMember.value = member;
}

function onSuccessfullGameSelection() {
  selectingGameMember.value = null;
  load();
}

onMounted(load);
</script>

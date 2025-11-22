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
      <q-btn flat icon="refresh" round @click="load" />
    </div>
  </div>

  <!-- Loading -->
  <q-linear-progress v-if="loading" indeterminate class="q-mb-md" />

  <ErrorDisplay v-if="error" :error="error" class="q-mb-md" />

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
      <q-card flat bordered class="fit" v-if="showPlayerGrid">
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
</template>

<script setup lang="ts">
import { computed, Ref, ref } from 'vue';
import { TLeague, TLeagueMember, TSeason } from 'src/types';
import { api } from 'boot/axios';
import ErrorDisplay from 'components/base/ErrorDisplay.vue';
import KennerButton from 'components/base/KennerButton.vue';
import ManageLeagueEditGame from 'components/league/manager/ManageLeagueEditGame.vue';
import ManageLeagueSelectGame from 'components/league/manager/ManageLeagueSelectGame.vue';

const props = defineProps<{
  load: () => void;
  league: Ref<TLeague | null>;
  season: Ref<TSeason | null>;

}>();

const loading = ref(false);
const error = ref<string | null>(null);

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
    await props.load();
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
  props.load();
}

function onSuccessfulGameEdit() {
  editingGameMember.value = null;
  props.load();
}

</script>

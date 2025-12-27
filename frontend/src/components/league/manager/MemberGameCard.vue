<template>
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
        >
          <q-tooltip>Remove Ban</q-tooltip>
        </q-btn>
      </q-chip>
      <q-chip
        v-else-if="member.has_banned"
        outline
        square
        color="grey-7"
        text-color="grey-7"
        icon="skip_next"
        class="q-ml-sm"
      >
        Ban Skipped
        <q-btn
          flat
          round
          dense
          size="xs"
          icon="close"
          class="q-ml-xs"
        >
          <q-tooltip>Remove Skip</q-tooltip>
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
        @click="$emit('add-game', member)"
      />
      <KennerButton
        v-if="!member.my_banned_game"
        outline
        dense
        color="red-7"
        icon="block"
        label="Ban Game"
        class="q-px-sm"
        @click="$emit('ban-game', member)"
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
        @click="$emit('set-active', member.profile)"
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
                    @click="$emit('edit-game', { member, selGame })"
                  >
                    <q-tooltip>Edit Settings</q-tooltip>
                  </q-btn>
                  <q-btn
                    flat
                    dense
                    round
                    :color="
                      hasResult(selGame) ? 'secondary' : 'primary'
                    "
                    :icon="
                      hasResult(selGame)
                        ? 'edit_note'
                        : 'post_add'
                    "
                    size="sm"
                    @click="
                      () =>
                        hasResult(selGame)
                          ? $emit('edit-result', selGame.id)
                          : $emit('post-result', selGame)
                    "
                  >
                    <q-tooltip>{{
                      hasResult(selGame)
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
                    @click="$emit('delete-game', { member, selGame })"
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
              label="Settings"
              header-class="text-weight-bold text-grey-7 bg-grey-1"
            >
              <template #header>
                <q-item-section avatar>
                  <q-icon
                    name="tune"
                    :color="selGame.selected_options?.length > 0 ? 'primary' : 'grey-7'"
                  />
                </q-item-section>
                <q-item-section>
                  <div class="text-weight-bold text-grey-7">Settings</div>
                </q-item-section>
              </template>
              <q-card-section class="bg-white q-pa-md">
                <GameSettingsDisplay
                  :selectedOptions="selGame.selected_options"
                />
              </q-card-section>
            </q-expansion-item>
            <q-separator />
            <q-expansion-item
              dense
              label="Match Result"
              header-class="text-weight-bold text-grey-7 bg-grey-1"
            >
              <template #header>
                <q-item-section avatar>
                  <q-icon
                    name="emoji_events"
                    :color="hasResult(selGame) ? 'secondary' : 'grey-7'"
                  />
                </q-item-section>
                <q-item-section>
                  <div class="text-weight-bold text-grey-7">Match Result</div>
                </q-item-section>
              </template>
              <q-card-section class="bg-white q-pa-md">
                <MatchResult
                  v-if="hasResult(selGame)"
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

<script setup lang="ts">
import KennerButton from 'components/base/KennerButton.vue';
import GameSettingsDisplay from 'components/game/selectedGame/GameSettingsDisplay.vue';
import MatchResult from 'components/league/MatchResult.vue';
import type { TSeasonDto } from 'src/types';

const props = defineProps<{
  member: any;
  league: any;
  season: TSeasonDto | null;
  matchResultsBySelectedGameId: Record<number, any[]>;
}>();

defineEmits([
  'add-game',
  'ban-game',
  'set-active',
  'edit-game',
  'edit-result',
  'post-result',
  'delete-game'
]);

function hasResult(selGame: any) {
  const results = props.matchResultsBySelectedGameId[selGame.id];
  return Array.isArray(results) && results.length > 0;
}
</script>

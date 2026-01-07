<template>
  <q-dialog
    :model-value="!!activeForm"
    @update:model-value="$emit('close')"
    persistent
  >
    <div v-if="activeForm" style="min-width: 320px; max-width: 90vw">
      <!-- Edit Game -->
      <FormLayout v-if="activeForm.type === 'edit'" @onClose="$emit('close')">
        <template #head>
          Edit Game
          <span class="text-primary">{{ activeForm.selGame.game_name }}</span>
          for
          <span class="text-primary">{{ activeForm.member.profile_name }}</span>
        </template>
        <GameSettingsEditor
          :leagueId="league.id"
          :profileId="activeForm.member.profile"
          :gameId="activeForm.selGame.game"
          :selectedGameId="activeForm.selGame.id"
          @onSuccess="$emit('success')"
        />
      </FormLayout>

      <!-- Select Game -->
      <FormLayout v-if="activeForm.type === 'add'" @onClose="$emit('close')">
        <template #head>
          Select Game for
          <span class="text-primary">{{ activeForm.member.profile_name }}</span>
        </template>
        <GameSelectionView
          manageOnly
          :leagueId="league.id"
          :profileId="activeForm.member.profile"
          @onSuccess="$emit('success')"
        />
      </FormLayout>

      <!-- Ban Game -->
      <FormLayout v-if="activeForm.type === 'ban'" @onClose="$emit('close')">
        <template #head>
          Ban Game for
          <span class="text-primary">{{ activeForm.member.profile_name }}</span>
        </template>
        <BanGameForm
          :league="league"
          :member="activeForm.member"
          @onSuccess="$emit('success')"
        />
      </FormLayout>

      <!-- Post Result -->
      <FormLayout v-if="activeForm.type === 'post-result'" @onClose="$emit('close')">
        <template #head>
          Post Result for
          <span class="text-primary">{{ activeForm.selGame.game_name }}</span>
        </template>
        <MatchResultForm
          :selectedGameId="activeForm.selGame.id"
          :leagueId="league.id"
          @submitted="$emit('success')"
        />
      </FormLayout>
    </div>
  </q-dialog>
</template>

<script setup lang="ts">
import FormLayout from 'components/league/manager/FormLayout.vue';
import GameSelectionView from 'components/game/selectedGame/GameSelectionView.vue';
import GameSettingsEditor from 'components/game/selectedGame/GameSettingsEditor.vue';
import MatchResultForm from 'components/league/MatchResultForm.vue';
import BanGameForm from 'components/game/selectedGame/BanGameForm.vue';
import type { TLeagueDto, TSeasonParticipantDto, TSelectedGameDto } from 'src/types';

export type TActiveForm =
  | { type: 'edit'; member: TSeasonParticipantDto; selGame: TSelectedGameDto }
  | { type: 'add'; member: TSeasonParticipantDto }
  | { type: 'ban'; member: TSeasonParticipantDto }
  | { type: 'post-result'; selGame: TSelectedGameDto };

defineProps<{
  league: TLeagueDto;
  activeForm: TActiveForm | null;
}>();

defineEmits(['close', 'success']);
</script>

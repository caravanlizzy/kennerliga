<template>
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
    @update:model-value="$emit('close')"
    persistent
  >
    <div style="min-width: 320px; max-width: 90vw">
      <FormLayout v-if="editingGame" @onClose="$emit('close')">
        <template #head>
          Edit Game
          <span class="text-primary">{{ editingGame.selGame?.game_name }}</span>
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
          @onSuccess="$emit('success-edit')"
        />
      </FormLayout>

      <FormLayout v-if="selectingGameMember" @onClose="$emit('close')">
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
          @onSuccess="$emit('success-submit')"
        />
      </FormLayout>

      <FormLayout v-if="banningGameMember" @onClose="$emit('close')">
        <template #head>
          Ban Game for
          <span class="text-primary">{{ banningGameMember.profile_name }}</span>
        </template>
        <BanGameForm
          :league="league"
          :member="banningGameMember"
          @onSuccess="$emit('success-submit')"
        />
      </FormLayout>

      <FormLayout v-if="postResultForSelGame" @onClose="$emit('close')">
        <template #head>
          Post Result for
          <span class="text-primary">{{ postResultForSelGame.game_name }}</span>
        </template>
        <MatchResultForm
          :selectedGameId="postResultForSelGame.id"
          :leagueId="league.id"
          @submitted="$emit('success-result')"
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

defineProps<{
  league: any;
  editingGame: any | null;
  selectingGameMember: any | null;
  banningGameMember: any | null;
  postResultForSelGame: any | null;
  editResultForSelGameId: number | null;
}>();

defineEmits(['close', 'success-submit', 'success-edit', 'success-result']);
</script>

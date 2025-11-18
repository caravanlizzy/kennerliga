<template>
  <div
    v-if="editingGameMember"
    class="q-pa-md q-mt-md bg-grey-1 rounded-borders col-12"
  >
    <div class="row items-center justify-between q-mb-sm">
      <div class="text-h6 text-weight-medium">
        Edit Game
        <span class="text-primary">{{
            editingGameMember.selected_game?.game_name
          }}</span>
        for
        <span class="text-primary">{{
            editingGameMember.profile_name.replace('_profile', '')
          }}</span>
      </div>
      <q-btn
        dense
        flat
        round
        icon="close"
        color="grey-7"
        @click="emit('onClose')"
      />
    </div>
    <GameEditor
      :leagueId="league.id"
      :profileId="editingGameMember.profile"
      :gameId="editingGameMember.selected_game.game"
      :selectedGameId="editingGameMember.selected_game.id"
    />
  </div>

</template>
<script setup lang="ts">
import GameEditor from 'components/game/selectedGame/GameEditor.vue';
import { TLeagueMember } from 'src/types';

defineProps<{editingGameMember: TLeagueMember}>();
const emit = defineEmits(['onClose']);
</script>

<template>
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
        @click="emit('onClose')"
      />
    </div>

    <q-separator class="q-mb-md" />

    <GameSelector
      manageOnly
      :leagueId="league.id"
      :profileId="selectingGameMember!.profile"
      @onSuccess="onSuccessfulGameSubmit"
    />
  </div>
</template>
<script setup lang="ts">
import GameSelector from 'components/game/selectedGame/GameSelector.vue';
import { TLeagueMember } from 'src/types';

defineProps<{
  selectingGameMember: TLeagueMember;
  league: any;
  onSuccessfulGameSubmit: () => void;
}>();
const emit = defineEmits(['onClose']);
</script>

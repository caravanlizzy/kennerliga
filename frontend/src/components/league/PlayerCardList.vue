<template>
  <div class="league-card q-pa-md">
    <div class="text-h6">Spielauswahl</div>
    <div :class="containerClass" >
      <div
        v-for="(member, index) in members"
        :key="member.id"
        class="player-card"
      >
        <PlayerCard
          :status="status"
          :member="member"
          :isActive="member.is_active_player"
          :isBanning="isBanning(member)"
          :isBannable="isBannable(member)"
          :index="index"
        />
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { useResponsive } from 'src/composables/reponsive';
import { computed } from 'vue';
import PlayerCard from 'components/league/PlayerCard.vue';
import { useUserStore } from 'stores/userStore';
import { TLeagueMember } from 'src/types';

const props = defineProps<{
  members: any[];
  status: string;
  activePlayer: string|undefined;
}>();

const { isMobile } = useResponsive();
const { user } = useUserStore();

const containerClass = computed(() =>
  isMobile ? 'column-reverse' : 'player-grid'
);

function isBannable(member: TLeagueMember): boolean {
  if (props.status !== 'BANNING') return false;
  if (user?.username !== props.activePlayer) return false;
  return !member.is_active_player;
}

function isBanning(member: TLeagueMember): boolean {
  if (props.status !== 'BANNING') return false;
  return member.is_active_player;
}
</script>

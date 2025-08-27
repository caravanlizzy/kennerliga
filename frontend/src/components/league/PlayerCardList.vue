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
          :status="leagueStatus"
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
import { storeToRefs } from 'pinia';
import { useLeagueStore } from 'stores/leagueStore';


const { isMobile } = useResponsive();
const {leagueStatus, members, isMeActivePlayer } = storeToRefs(useLeagueStore());

const containerClass = computed(() =>
  isMobile ? 'column-reverse' : 'player-grid'
);

function isBannable(member: TLeagueMember): boolean {
  // only bannable if leagueStatus is in banning phase
  if (leagueStatus.value !== 'BANNING') return false;

  // only bannable if *I* am the active player
  if (!isMeActivePlayer.value) return false;

  // I can ban others, but not myself
  return !member.is_active_player;
}

function isBanning(member: TLeagueMember): boolean {
  return leagueStatus.value === 'BANNING' && member.is_active_player;
}

</script>

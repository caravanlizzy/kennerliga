<template>
  <div class="league-card">
    <div class="text-h6">Spielauswahl</div>
    <div :class="containerClass" >
      <div
        v-for="member in members"
        :key="member.id"
        class="player-card"
      >
        <PlayerCard
          :member="member"
        />
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { useResponsive } from 'src/composables/reponsive';
import { computed } from 'vue';
import PlayerCard from 'components/league/PlayerCard.vue';
import { storeToRefs } from 'pinia';
import { useLeagueStore } from 'stores/leagueStore';


const { isMobile } = useResponsive();
const { members } = storeToRefs(useLeagueStore());

const containerClass = computed(() =>
  isMobile ? 'column-reverse' : 'player-grid'
);



</script>

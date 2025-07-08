<template>
  <!-- Status Bar -->
  <div
    class="q-pa-lg column justify-center items-center text-primary border border-primary rounded-borders"
  >
    <div class="text-h6 text-uppercase text-weight-bold q-mb-sm">
      {{ statusNoun }}
    </div>

    <div class="text-subtitle1 text-center">
      <span class="text-primary text-weight-bold">
        {{ activePlayer?.username }}
      </span>
      <span v-if="status === 'PICKING' || status === 'BANNING'" class="q-mx-xs"
        >muss ein Spiel
      </span>
      <span
        class="text-weight-bold"
        :class="{
          'text-accent': league?.status === 'BANNING',
          'text-secondary': league?.status === 'PICKING',
        }"
      >
        {{ statusVerb }}
      </span>
    </div>
    <q-btn
      v-if="isPlayerBanning"
      color="accent"
      outline
      class="q-mt-sm"
      @click="banNothin"
    >
      Banne nichts
    </q-btn>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

type LeagueStatus = 'PICKING' | 'BANNING' | 'PLAYING' | 'DONE';



const props = defineProps<{
  league: any;
  activePlayer: any;
  status: LeagueStatus;
  isPlayerBanning: boolean;
}>();


const statusMap: Record<LeagueStatus, { noun?: string; verb?: string }> = {
  PICKING: { noun: 'Spielauswahl', verb: 'auswählen' },
  BANNING: { noun: 'Bannen', verb: 'bannen' },
  PLAYING: { noun: 'Spiele laufen' },
  DONE: { noun: 'Beendet' },
};

const statusNoun = computed(
  () => statusMap[props.league?.status as LeagueStatus]?.noun ?? ''
);

const statusVerb = computed(
  () => statusMap[props.league?.status as LeagueStatus]?.verb ?? ''
);


</script>

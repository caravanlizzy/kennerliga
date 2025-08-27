<template>
  <!-- Status Bar -->
  <div
    class="q-pa-lg column justify-center items-center text-primary border border-primary rounded-borders"
  >
    <div class="text-h6 text-uppercase text-italic text-weight-bold q-mb-sm">
      {{ currentStatusNoun }}
    </div>

    <div class="text-subtitle1 text-center">
      <span class="text-primary text-weight-bold">
        {{ activePlayer?.username }}
      </span>
      <span v-if="leagueStatus === 'PICKING' || leagueStatus === 'BANNING'" class="q-mx-xs"
        >muss ein Spiel
      </span>
      <span
        class="text-weight-bold"
        :class="{
          'text-accent': leagueStatus === 'BANNING',
          'text-secondary': leagueStatus === 'PICKING',
        }"
      >
        {{ statusVerb }}
      </span>
    </div>
    <q-btn
      v-if="isMeBanningGame"
      color="accent"
      outline
      class="q-mt-sm"
      @click="banNothing"
    >
      Banne nichts
    </q-btn>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useLeagueStore } from 'stores/leagueStore';

type LeagueStatus = 'PICKING' | 'BANNING' | 'PLAYING' | 'DONE';

const { leagueStatus, activePlayer, isMeBanningGame, banNothing } = useLeagueStore();


const statusMap: Record<LeagueStatus, { noun?: string; verb?: string }> = {
  PICKING: { noun: 'Spielauswahl', verb: 'auswählen' },
  BANNING: { noun: 'Bannen', verb: 'bannen' },
  PLAYING: { noun: 'Spiele laufen' },
  DONE: { noun: 'Beendet' },
};

const currentStatusNoun = computed(
  () => statusMap[leagueStatus as LeagueStatus]?.noun ?? ''
);

const statusVerb = computed(
  () => statusMap[leagueStatus as LeagueStatus]?.verb ?? ''
);


</script>

<template>
  <!-- Status Bar -->
  <div
    class="column justify-center items-center text-primary border border-primary rounded-borders"
  >
    <div class="text-h6 text-weight-bold q-mb-sm">
      <span>
        {{ currentStatusNoun.toUpperCase() }}
      </span>
      <div class="text-subtitle1 text-weight-regular text-italic text-center">
        <span class="text-primary">
          {{ activePlayer?.username }}
        </span>
        <span v-if="leagueStatus === 'PICKING' || leagueStatus === 'BANNING'">
          to
        </span>
        <span
          :class="{
            'text-accent': leagueStatus === 'BANNING',
            'text-secondary':
              leagueStatus === 'PICKING' || leagueStatus === 'REPICKING',
          }"
        >
          {{ statusVerb }}
        </span>
      </div>
    </div>

    <q-btn
      v-if="isMeBanningGame"
      color="accent"
      outline
      class="q-mt-sm"
      @click="banNothing"
    >
      Do not ban
    </q-btn>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useLeagueStore } from 'stores/leagueStore';
import { storeToRefs } from 'pinia';
import { TLeagueStatus } from 'src/types';

const { leagueStatus, activePlayer, isMeBanningGame } = storeToRefs(
  useLeagueStore()
);

const { banNothing } = useLeagueStore();

const statusMap: Record<TLeagueStatus, { noun?: string; verb?: string }> = {
  PICKING: { noun: 'Game Selection Phase', verb: 'select' },
  REPICKING: { noun: 'Game Reselection', verb: 'reselect' },
  BANNING: { noun: 'Ban Phase', verb: 'ban' },
  PLAYING: { noun: 'Games running' },
  DONE: { noun: 'League finished' },
};

const currentStatusNoun = computed(
  () => statusMap[leagueStatus.value]?.noun ?? ''
);

const statusVerb = computed(() => statusMap[leagueStatus.value]?.verb ?? '');
</script>

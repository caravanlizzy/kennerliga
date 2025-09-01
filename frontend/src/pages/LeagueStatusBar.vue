<template>
  <!-- Status Bar -->
  <div class="column bg-grey-3">
    <!-- Main Title -->
    <div class="text-h5 text-weight-bold text-primary text-center">
      {{ currentStatusNoun.toUpperCase() }}
    </div>

    <!-- Subline: user + verb centered, button right -->
    <div class="row items-center justify-between q-mt-xs">
      <!-- Centered block -->
      <div class="row items-center justify-center col text-subtitle1 text-weight-regular text-italic">
        <q-chip class="text-white" :class="activePlayer?.colorClass">
          {{ activePlayer?.username }}
        </q-chip>

        <span v-if="leagueStatus === 'PICKING' || leagueStatus === 'BANNING'">
          to
        </span>

        <span
          class="q-ml-xs text-weight-medium text-uppercase"
          :class="{
            'text-accent': leagueStatus === 'BANNING',
            'text-secondary': leagueStatus === 'PICKING' || leagueStatus === 'REPICKING',
          }"
        >
          {{ statusVerb }}
        </span>
      </div>
    </div>
    <!-- Reusable Action Bar -->
    <ActionBar v-if="isMeActivePlayer"/>
  </div>
</template>

<script setup lang="ts">
import { computed, h } from 'vue';
import { useLeagueStore } from 'stores/leagueStore';
import { storeToRefs } from 'pinia';
import { TLeagueStatus } from 'src/types';
import ActionBar from 'components/layout/ActionBar.vue';

const { leagueStatus, activePlayer, isMeBanningGame, isMeActivePlayer } = storeToRefs(
  useLeagueStore()
);

const { banNothing } = useLeagueStore();

const statusMap: Record<TLeagueStatus, { noun?: string; verb?: string }> = {
  PICKING: { noun: 'Game Selection Phase', verb: 'pick' },
  REPICKING: { noun: 'Game Reselection', verb: 'pick again' },
  BANNING: { noun: 'Ban Phase', verb: 'ban' },
  PLAYING: { noun: 'Games running' },
  DONE: { noun: 'League finished' },
};

const currentStatusNoun = computed(
  () => statusMap[leagueStatus.value]?.noun ?? ''
);

const statusVerb = computed(() => statusMap[leagueStatus.value]?.verb ?? '');
</script>

<style scoped lang="scss">
.status-borders {
  border-top: 4px solid $info;
  border-bottom: 4px solid $info;
}
</style>

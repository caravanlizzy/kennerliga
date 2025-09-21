<template>
  <!-- Status Bar -->
  <div class="column">
    <!-- Main Title -->
    <div class="text-h5 text-weight-bold text-primary text-center">
      {{ statusNoun.toUpperCase() }}
    </div>

    <ActionBar v-if="leagueStatus !== 'PLAYING'&& leagueStatus !=='DONE'"/>
  </div>
</template>

<script setup lang="ts">
import ActionBar from 'components/ui/ActionBar.vue';
import { storeToRefs } from 'pinia';
import { useLeagueStore } from 'stores/leagueStore';
const { statusNoun, leagueStatus } = storeToRefs(useLeagueStore());

</script>

<style scoped lang="scss">
.status-borders {
  border-top: 4px solid $info;
  border-bottom: 4px solid $info;
}
</style>

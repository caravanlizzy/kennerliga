<template>
  <ContentSection
    v-if="isMePickingGame && leagueId"
    title="Game Selection"
    color="primary"
    icon="ads_click"
    v-bind="$attrs"
  >
    <GameSelectionView
      :leagueId="leagueId"
      :profileId="myProfileId"
      :memberCount="memberCount"
      @onSuccess="updateLeagueData"
    />
  </ContentSection>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import ContentSection from 'components/base/ContentSection.vue';
import GameSelectionView from 'components/game/selectedGame/GameSelectionView.vue';
import { useMyLeagueStore } from 'src/composables/myLeague';

const myLeagueStore = useMyLeagueStore();
const { isMePickingGame, myProfileId, leagueId, members } = storeToRefs(myLeagueStore);
const { updateLeagueData } = myLeagueStore;

const memberCount = computed(() => (members.value ?? []).length);
</script>

<style scoped lang="scss">
</style>

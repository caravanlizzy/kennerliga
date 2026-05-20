<template>
  <ContentSection
    title="League Standings"
    color="info"
    icon="leaderboard"
    bordered
    expandable
    v-model:is-opened="isOpened"
    class="league-section"
  >
    <LeagueStandings />
  </ContentSection>
</template>

<script setup lang="ts">
import { ref, watchEffect } from 'vue';
import { storeToRefs } from 'pinia';
import LeagueStandings from 'components/league/LeagueStandings.vue';
import { useMyLeagueStore } from 'src/composables/myLeague';
import ContentSection from 'components/base/ContentSection.vue';

const { selectedGamesWithResults } = storeToRefs(useMyLeagueStore());

const isOpened = ref(false);

watchEffect(() => {
  isOpened.value = selectedGamesWithResults.value.length > 0;
});
</script>

<style scoped>
.league-section {
  margin-bottom: 16px;
}
</style>

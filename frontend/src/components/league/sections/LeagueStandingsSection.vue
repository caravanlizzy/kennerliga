<template>
  <ContentSection
    title="League Standings"
    color="info"
    icon="leaderboard"
    expandable
    v-model:is-opened="isOpened"
    v-bind="$attrs"
    class="league-section"
  >
    <LeagueStandings />
  </ContentSection>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import LeagueStandings from 'components/league/LeagueStandings.vue';
import ContentSection from 'components/base/ContentSection.vue';

const isOpened = ref(true);
</script>

<style scoped lang="scss">
</style>

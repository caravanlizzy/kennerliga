<template>
  <ContentSection
    title="League Standings"
    color="info"
    icon="leaderboard"
    v-bind="$attrs"
    class="league-section"
  >
    <LeagueStandings />
  </ContentSection>
</template>

<script setup lang="ts">
import LeagueStandings from 'components/league/LeagueStandings.vue';
import ContentSection from 'components/base/ContentSection.vue';
</script>

<style scoped lang="scss">
</style>

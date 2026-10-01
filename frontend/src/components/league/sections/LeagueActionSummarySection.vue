<template>
  <ContentSection
    title="Action Summary"
    color="primary"
    icon="history"
    expandable
    v-model:is-opened="isOpened"
    v-bind="$attrs"
    class="league-section"
  >
    <LeagueActionSummary :league-id="leagueData?.id || leagueId" />
  </ContentSection>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { storeToRefs } from 'pinia';
import ContentSection from 'components/base/ContentSection.vue';
import LeagueActionSummary from 'components/league/LeagueActionSummary.vue';
import { useMyLeagueStore } from 'src/composables/myLeague';

const { leagueId, leagueData } = storeToRefs(useMyLeagueStore());

const isOpened = ref(true);
</script>

<style scoped lang="scss">
</style>

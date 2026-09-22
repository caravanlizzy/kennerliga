<template>
  <ContentSection
    v-if="leagueStatus === 'PLAYING'"
    title="Report Match Results"
    color="accent"
    icon="publish"
    expandable
    v-model:is-opened="isOpened"
    v-bind="$attrs"
    class="league-section"
  >
    <MatchResultTabs />
  </ContentSection>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { storeToRefs } from 'pinia';
import ContentSection from 'components/base/ContentSection.vue';
import MatchResultTabs from 'components/league/MatchResultTabs.vue';
import { useMyLeagueStore } from 'src/composables/myLeague';

const { leagueStatus } = storeToRefs(useMyLeagueStore());

const isOpened = ref(true);
</script>

<style scoped lang="scss">
</style>

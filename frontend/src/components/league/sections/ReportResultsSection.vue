<template>
  <ContentSection
    v-if="leagueStatus === 'PLAYING'"
    title="Report Results"
    color="accent"
    icon="publish"
    v-bind="$attrs"
    v-model:is-opened="isOpened"
    expandable
    class="league-section"
  >
    <MatchResultTabs />
  </ContentSection>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { storeToRefs } from 'pinia';
import ContentSection from 'components/base/ContentSection.vue';
import MatchResultTabs from 'components/league/MatchResultTabs.vue';
import { useMyLeagueStore } from 'src/composables/myLeague';
import { useActionBar } from 'src/composables/actionBar';

const { leagueStatus } = storeToRefs(useMyLeagueStore());
const { reset } = useActionBar();

const isOpened = ref(false);

watch(
  leagueStatus,
  (status) => {
    isOpened.value = status === 'PLAYING';
    if (status === 'PLAYING') {
      reset();
    }
  },
  { immediate: true }
);
</script>

<style scoped lang="scss">
</style>

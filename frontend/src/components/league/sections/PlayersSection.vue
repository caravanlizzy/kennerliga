<template>
  <ContentSection
    title="Players & Game Picks"
    color="secondary"
    icon="groups"
    v-bind="$attrs"
    class="league-section"
  >
    <PlayerCard :all-members="members" />
  </ContentSection>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import ContentSection from 'components/base/ContentSection.vue';
import PlayerCard from 'components/league/PlayerCard.vue';
import { useMyLeagueStore } from 'src/composables/myLeague';

const { members } = storeToRefs(useMyLeagueStore());
</script>

<style scoped lang="scss">
</style>

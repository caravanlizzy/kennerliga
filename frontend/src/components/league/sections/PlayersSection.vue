<template>
  <ContentSection
    title="Games - Picks and Bans"
    color="secondary"
    icon="groups"
    v-model:is-opened="isOpened"
    expandable
    bordered
    class="league-section"
  >
    <PlayerCard :all-members="members" />
  </ContentSection>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { storeToRefs } from 'pinia';
import ContentSection from 'components/base/ContentSection.vue';
import PlayerCard from 'components/league/PlayerCard.vue';
import { useMyLeagueStore } from 'src/composables/myLeague';

const { members } = storeToRefs(useMyLeagueStore());

const isOpened = ref(true);
</script>

<style scoped>
.league-section {
  margin-bottom: 16px;
}
</style>

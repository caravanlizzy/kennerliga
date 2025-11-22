<template>
  <div>Results</div>
  <LoadingSpinner v-if="loading" />
  <template
    v-else
    v-for="selectedGame of nonNullSelectedGames"
    :key="selectedGame.id"
  >
    <MatchResult
      v-if="league.hasSelectedGameResult(selectedGame.id)"
      :selectedGame="selectedGame"
    />
    <MatchResultForm
      v-else
      :selectedGameId="selectedGame.id"
    />
  </template>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { storeToRefs } from 'pinia';

import MatchResult from 'components/league/MatchResult.vue';
import MatchResultForm from 'components/league/MatchResultForm.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import { useLeagueStore } from 'stores/leagueStore';

const props = defineProps<{
  selectedGames: Array<any>;
}>();

const league = useLeagueStore();
const { loading } = storeToRefs(league);

const nonNullSelectedGames = computed(() =>
  props.selectedGames?.filter(g => g !== null)
);

onMounted(async () => {
  await league.init();
});
</script>

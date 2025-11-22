<template>
  <!-- Loading -->
  <LoadingSpinner v-if="loading" />

  <ErrorDisplay v-if="error" :error="error" class="q-mb-md" />

  <ManageLeagueMembers
    v-if="!loading && !error"
    :load="load"
    :league="league"
    :season="season"
  />

  <!--  <LeagueResultUpload />-->
  <ManageLeagueResults
    v-if="!loading && !error"
    :selectedGames="selectedGames"
  />
</template>

<script setup lang="ts">
import ManageLeagueMembers from 'components/league/manager/ManageLeagueMembers.vue';
import ManageLeagueResults from 'components/league/manager/ManageLeagueResults.vue';
import { fetchLeagueDetails } from 'src/services/leagueService';
import { fetchSeason } from 'src/services/seasonService';
import ErrorDisplay from 'components/base/ErrorDisplay.vue';
import { computed, onMounted, ref } from 'vue';
import { TLeague, TSeason } from 'src/types';
import { useRoute } from 'vue-router';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';

const route = useRoute();

const league = ref<TLeague|null>(null);
const season = ref<TSeason | null>(null);

const loading = ref(false);
const error = ref<string | null>(null);

async function load() {
  loading.value = true;
  error.value = null;
  try {
    const leagueId = Number(route.params.id);
    league.value = await fetchLeagueDetails(leagueId);
    await new Promise((resolve) => setTimeout(resolve, 2000));
    if (!league.value) throw new Error('Failed to load league data.');
    season.value = await fetchSeason(league.value.season);
  } catch (e: any) {
    error.value = e?.message || 'Failed to load league/season data.';
  } finally {
    loading.value = false;
  }
}

const selectedGames = computed(() =>
  league.value?.members
    .map((m) => m.selected_game)
);

onMounted(load);
</script>

<template>
<q-tabs
  v-model="currentFormSelectedGameId"
  active-color="white"
  active-bg-color="primary"
  indicator-color="primary"
  :vertical="isMobile"
>
  <q-tab
    v-for="selectedGame in selectedGamesFetchedEmpty"
    :key="selectedGame.id"
    :name="selectedGame.id"
    class="text-weight-medium"
  >
    {{ truncateString(selectedGame.game_name) }}
  </q-tab>
</q-tabs>

  <!-- Match Result Entry Form -->
  <MatchResultForm
    v-if="currentFormSelectedGameId"
    @submitted="handleSubmit"
    :selected-game-id="currentFormSelectedGameId"
    :leagueId="user.myCurrentLeagueId"
  />
</template>

<script setup lang="ts">
import MatchResultForm from 'components/league/MatchResultForm.vue';
import { storeToRefs } from 'pinia';
import { useLeagueStore } from 'stores/leagueStore';
import { ref } from 'vue';
import { useResponsive } from 'src/composables/responsive';
import { truncateString } from 'src/helpers';
import { useUserStore } from 'stores/userStore';

const { user } = storeToRefs(useUserStore());
const myLeagueStore = useLeagueStore(user.value.myCurrentLeagueId)();
const { selectedGamesFetchedEmpty } = storeToRefs(myLeagueStore);
const { refreshResultsForGame } = myLeagueStore;
const { isMobile } = useResponsive();

const currentFormSelectedGameId = ref(null);

function handleSubmit(selectedGameId: number) {
  currentFormSelectedGameId.value = null;
  refreshResultsForGame(selectedGameId);
}
</script>

<style scoped></style>

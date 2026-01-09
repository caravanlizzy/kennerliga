<template>
  <q-page class="bg-white">
    <div class="q-pa-md row items-center justify-between no-wrap border-bottom-subtle">
      <div class="text-h5 text-weight-bold text-dark">
        Leaderboard
      </div>
      <div style="min-width: 100px">
        <KennerSelect
          v-model="selectedYear"
          :options="availableYears"
          class="full-width"
          emit-value
          map-options
        />
      </div>
    </div>
    <LeaderBoard :year="selectedYear" />
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import LeaderBoard from 'components/season/LeaderBoard.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import { fetchAvailableYears, fetchCurrentSeasonId, fetchSeason } from 'src/services/seasonService';
import { useUiStore } from 'stores/uiStore';

const uiStore = useUiStore();
const selectedYear = ref(new Date().getFullYear());
const availableYears = ref<number[]>([]);

onMounted(async () => {
  uiStore.activeTab = 'leaderboard';

  const [years, currentSeasonId] = await Promise.all([
    fetchAvailableYears(),
    fetchCurrentSeasonId(),
  ]);

  availableYears.value = years;

  if (currentSeasonId) {
    const season = await fetchSeason(currentSeasonId);
    if (season) {
      selectedYear.value = season.year;
    }
  } else if (availableYears.value.length > 0) {
    selectedYear.value = availableYears.value[0];
  }
});
</script>

<style scoped>
.border-bottom-subtle {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}
</style>

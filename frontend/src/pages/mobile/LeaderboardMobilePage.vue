<template>
  <q-page class="bg-white">
    <div class="q-pa-md row items-center justify-between no-wrap border-bottom-subtle">
      <div class="row items-center no-wrap q-gutter-x-sm">
        <q-icon name="stars" size="sm" color="primary" />
        <SmoothSwitch
          v-model="showAllLeagues"
          :options="[
            { label: 'Highest', value: false },
            { label: 'All', value: true }
          ]"
        />
      </div>
      <div class="row items-center no-wrap q-gutter-x-sm">
        <div style="min-width: 80px">
          <KennerSelect
            v-model="selectedYear"
            :options="availableYears"
            class="full-width"
            label="Year"
            emit-value
            map-options
            dense
          />
        </div>
      </div>
    </div>
    <LeaderBoard v-model:show-all-leagues="showAllLeagues" :year="selectedYear" />
  </q-page>
</template>

<script setup lang="ts">
defineOptions({ name: 'LeaderboardMobilePage' });
import { ref, onMounted } from 'vue';
import LeaderBoard from 'components/season/LeaderBoard.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import SmoothSwitch from 'components/base/SmoothSwitch.vue';
import { fetchAvailableYears, fetchCurrentSeasonId, fetchSeason } from 'src/services/seasonService';

const selectedYear = ref(new Date().getFullYear());
const showAllLeagues = ref(false);
const availableYears = ref<number[]>([]);

onMounted(async () => {
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

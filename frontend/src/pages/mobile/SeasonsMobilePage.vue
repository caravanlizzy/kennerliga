<template>
  <q-page class="bg-white">
    <div
      class="q-pa-md row items-center justify-between no-wrap border-bottom-subtle"
    >
      <div class="text-h5 text-weight-bold text-dark">Seasons</div>
      <div
        v-if="!loading || selectedSeasonId"
        class="row no-wrap items-center q-gutter-x-sm"
      >
        <div style="min-width: 80px">
          <KennerSelect
            v-model="selectedSeasonYear"
            :options="seasonYearOptions"
            dense
            label="Year"
            emit-value
            map-options
            :disable="loading && !selectedSeasonId"
          />
        </div>
        <div style="min-width: 100px">
          <KennerSelect
            v-model="selectedSeasonMonth"
            :options="seasonMonthOptions"
            dense
            label="Month"
            emit-value
            map-options
            :disable="loading && !selectedSeasonId"
          />
        </div>
        <q-icon name="military_tech" size="sm" color="primary" />
      </div>
    </div>
    <SeasonStandings v-if="selectedSeasonId" :seasonId="selectedSeasonId" />
    <div v-else-if="loading" class="flex flex-center q-pa-xl">
      <LoadingSpinner text="Loading seasons..." />
    </div>
  </q-page>
</template>

<script setup lang="ts">
defineOptions({ name: 'SeasonsMobilePage' });

import { onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import SeasonStandings from 'components/season/SeasonStandings.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import { useHomeSeasonStore } from 'stores/homeSeasonStore';

const homeSeasonStore = useHomeSeasonStore();

const {
  selectedSeasonYear,
  selectedSeasonMonth,
  loading,
  seasonYearOptions,
  seasonMonthOptions,
  selectedSeasonId,
} = storeToRefs(homeSeasonStore);

onMounted(() => {
  void homeSeasonStore.init();
});
</script>

<style scoped>
.border-bottom-subtle {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}
</style>

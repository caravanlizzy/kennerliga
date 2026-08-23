<template>
  <div class="player-statistics">
    <div class="section-header row items-center no-wrap q-mb-md">
      <div class="section-header__icon">
        <q-icon name="groups" color="primary" size="20px" />
      </div>
      <div class="column">
        <div class="text-h6 text-weight-bolder text-dark line-height-1">Players</div>
        <div class="text-caption text-grey-6">
          Rankings, records &amp; superlatives across every player.
        </div>
      </div>
    </div>

    <div v-if="loadingOverview" class="row q-col-gutter-lg">
      <div v-for="i in 6" :key="i" class="col-12 col-lg-6">
        <q-skeleton type="rect" height="240px" class="rounded-borders" />
      </div>
    </div>

    <div v-else class="row q-col-gutter-lg">
      <div v-for="award in overview?.awards ?? []" :key="award.key" class="col-12 col-lg-6">
        <StatCategoryCard :category="award" />
      </div>
      <div
        v-for="category in overview?.categories ?? []"
        :key="category.key"
        class="col-12 col-lg-6"
      >
        <StatCategoryCard :category="category" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'PlayerStatistics' });

import { onMounted, ref, watch } from 'vue';
import StatCategoryCard from 'components/statistics/StatCategoryCard.vue';
import { fetchStatisticsOverview } from 'src/services/statisticsService';
import { TStatisticsOverview } from 'src/types';

const props = defineProps<{
  years: number[];
  playerCounts: string[] | undefined;
}>();

const overview = ref<TStatisticsOverview | null>(null);
const loadingOverview = ref(false);

async function loadOverview() {
  loadingOverview.value = true;
  try {
    overview.value = await fetchStatisticsOverview({
      years: props.years,
      playerCounts: props.playerCounts,
      // Large enough to cover every player in any realistic league, so the
      // category cards' "show all" expansion never needs a second request.
      topN: 200,
    });
  } finally {
    loadingOverview.value = false;
  }
}

watch(
  () => [props.years, props.playerCounts],
  () => {
    void loadOverview();
  },
  { deep: true }
);

onMounted(() => {
  void loadOverview();
});
</script>

<style scoped lang="scss">
// Section header that labels the "Players" side of the split stats layout.
.section-header {
  gap: 10px;

  &__icon {
    width: 38px;
    height: 38px;
    border-radius: 9px;
    background: rgba(99, 102, 241, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
}
</style>

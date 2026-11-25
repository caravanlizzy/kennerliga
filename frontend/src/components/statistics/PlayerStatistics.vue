<template>
  <div class="player-statistics">
    <div v-if="loadingOverview">
      <div
        class="section-header row items-center no-wrap"
        :class="isMobile ? 'q-mb-xs' : 'q-mb-md'"
      >
        <div
          class="section-header__icon"
          :class="isMobile ? 'section-header__icon--mobile' : ''"
        >
          <q-icon
            name="military_tech"
            color="primary"
            :size="isMobile ? '16px' : '20px'"
          />
        </div>
        <div class="column">
          <div
            class="text-weight-bolder text-dark line-height-1"
            :class="isMobile ? 'text-subtitle1' : 'text-h6'"
          >
            Performance Leaderboards
          </div>
          <div v-if="!isMobile" class="text-caption text-grey-6">
            Rankings across core competitive metrics
          </div>
        </div>
      </div>
      <div
        class="row"
        :class="[
          isMobile ? 'q-col-gutter-sm q-mb-md' : 'q-col-gutter-lg q-mb-xl',
        ]"
      >
        <div
          v-for="i in 6"
          :key="`sk-cat-${i}`"
          class="col-12 col-sm-6 col-lg-4"
        >
          <q-skeleton type="rect" height="240px" class="rounded-borders" />
        </div>
      </div>
    </div>

    <div v-else>
      <!-- Core Categories Section -->
      <div
        v-if="(overview?.categories ?? []).length > 0"
        :class="isMobile ? 'q-mb-md' : 'q-mb-xl'"
      >
        <div
          class="section-header row items-center no-wrap"
          :class="isMobile ? 'q-mb-xs' : 'q-mb-md'"
        >
          <div
            class="section-header__icon"
            :class="isMobile ? 'section-header__icon--mobile' : ''"
          >
            <q-icon
              name="military_tech"
              color="primary"
              :size="isMobile ? '16px' : '20px'"
            />
          </div>
          <div class="column">
            <div
              class="text-weight-bolder text-dark line-height-1"
              :class="isMobile ? 'text-subtitle1' : 'text-h6'"
            >
              Performance Leaderboards
            </div>
            <div v-if="!isMobile" class="text-caption text-grey-6">
              Rankings across win rate, average position, games played, records,
              and career score
            </div>
          </div>
        </div>

        <div
          class="row"
          :class="isMobile ? 'q-col-gutter-sm' : 'q-col-gutter-lg'"
        >
          <div
            v-for="category in overview?.categories ?? []"
            :key="category.key"
            class="col-12 col-sm-6 col-lg-4"
          >
            <StatCategoryCard :category="category" />
          </div>
        </div>
      </div>

      <!-- Awards Section -->
      <div
        v-if="(overview?.awards ?? []).length > 0"
        :class="isMobile ? 'q-mb-md' : 'q-mb-lg'"
      >
        <div
          class="section-header row items-center no-wrap"
          :class="isMobile ? 'q-mb-xs' : 'q-mb-md'"
        >
          <div
            class="section-header__icon awards-header-icon"
            :class="isMobile ? 'section-header__icon--mobile' : ''"
          >
            <q-icon
              name="emoji_events"
              color="amber-9"
              :size="isMobile ? '16px' : '20px'"
            />
          </div>
          <div class="column">
            <div
              class="text-weight-bolder text-dark line-height-1"
              :class="isMobile ? 'text-subtitle1' : 'text-h6'"
            >
              Awards &amp; Superlatives
            </div>
            <div v-if="!isMobile" class="text-caption text-grey-6">
              Playstyle achievements, ban habits, and game choices
            </div>
          </div>
        </div>

        <div
          class="row"
          :class="isMobile ? 'q-col-gutter-sm' : 'q-col-gutter-lg'"
        >
          <div
            v-for="award in overview?.awards ?? []"
            :key="award.key"
            class="col-12 col-sm-6 col-lg-4"
          >
            <StatCategoryCard :category="award" />
          </div>
        </div>
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
import { useResponsive } from 'src/composables/responsive';

const { isMobile } = useResponsive();

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

    &--mobile {
      width: 28px;
      height: 28px;
      border-radius: 6px;
    }

    &.awards-header-icon {
      background: rgba(245, 158, 11, 0.15);
    }
  }
}
</style>

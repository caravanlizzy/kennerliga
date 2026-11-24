<template>
  <q-page
    class="max-width-container q-mx-auto statistics-page"
    :class="isMobile ? 'q-pa-sm' : 'q-pa-md'"
  >
    <!-- Header -->
    <div
      class="stats-header-bar row items-center justify-between"
      :class="isMobile ? 'q-mb-sm' : 'q-mb-md'"
    >
      <div class="row items-center no-wrap">
        <div
          class="page-title-icon q-mr-sm"
          :class="isMobile ? 'page-title-icon--mobile' : ''"
        >
          <q-icon
            name="stars"
            color="primary"
            :size="isMobile ? '20px' : '24px'"
          />
        </div>
        <div>
          <div
            class="text-weight-bolder text-dark line-height-1"
            :class="isMobile ? 'text-subtitle1' : 'text-h5'"
          >
            Hall of Fame &amp; Records
          </div>
          <div v-if="!isMobile" class="text-caption text-grey-6 q-mt-xs">
            Historical season champions, league placements, and all-time records
          </div>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <q-tabs
      v-model="currentTab"
      dense
      class="text-grey-7 stats-tabs"
      :class="isMobile ? 'q-mb-sm stats-tabs--mobile' : 'q-mb-md'"
      active-color="primary"
      indicator-color="primary"
      :align="isMobile ? 'justify' : 'left'"
      narrow-indicator
      @update:model-value="onTabChange"
    >
      <q-tab
        name="hall-of-fame"
        icon="emoji_events"
        label="Hall of Fame &amp; Seasons"
      />
      <q-tab
        name="records"
        icon="military_tech"
        label="Global Records &amp; Metagame"
      />
    </q-tabs>

    <!-- Tab Panels -->
    <q-tab-panels
      v-model="currentTab"
      animated
      class="bg-transparent stats-tab-panels"
    >
      <!-- Tab 1: Hall of Fame & Seasons -->
      <q-tab-panel name="hall-of-fame" class="q-pa-none">
        <div
          class="filter-toolbar row items-center justify-between"
          :class="isMobile ? 'q-mb-sm' : 'q-mb-md'"
        >
          <div class="row items-center no-wrap q-gutter-x-sm">
            <SmoothSwitch
              v-model="showAllLeagues"
              :options="[
                { label: 'Highest', value: false },
                { label: 'All', value: true },
              ]"
            />
          </div>
          <div class="row items-center no-wrap q-gutter-x-sm">
            <div style="min-width: 120px">
              <KennerSelect
                v-model="selectedSeasonYear"
                :options="seasonYearOptions"
                class="full-width"
                label="Year"
                emit-value
                map-options
                dense
              />
            </div>
          </div>
        </div>

        <LeaderBoard
          v-model:show-all-leagues="showAllLeagues"
          :year="selectedSeasonYear"
        />
      </q-tab-panel>

      <!-- Tab 2: Global Records & Metagame -->
      <q-tab-panel name="records" class="q-pa-none">
        <div
          class="filter-toolbar row items-center justify-between"
          :class="isMobile ? 'q-mb-sm' : 'q-mb-md'"
        >
          <div
            class="filter-controls row items-center"
            :class="isMobile ? 'q-col-gutter-xs' : 'q-col-gutter-md'"
          >
            <!-- Player Count Filter -->
            <div class="filter-item row items-center">
              <KennerPlayerCountFilter
                v-model="selectedPlayerCounts"
                :available-counts="availablePlayerCounts"
                label="Players:"
              />
            </div>

            <!-- Years Multi-select Filter -->
            <div class="filter-item row items-center q-gutter-x-xs">
              <div
                class="row items-center text-caption text-weight-bold text-grey-8 filter-label"
              >
                <q-icon
                  name="calendar_today"
                  :size="isMobile ? '14px' : '16px'"
                  class="q-mr-xs text-primary"
                />
                <span v-if="!isMobile">Years:</span>
              </div>
              <q-select
                v-model="selectedOverviewYears"
                :options="overviewYearOptions"
                multiple
                clearable
                dense
                outlined
                options-dense
                placeholder="All Years"
                :display-value="
                  !selectedOverviewYears || selectedOverviewYears.length === 0
                    ? 'All Years'
                    : selectedOverviewYears
                        .slice()
                        .sort((a, b) => b - a)
                        .join(', ')
                "
                class="bg-white rounded-borders years-select"
                :class="isMobile ? 'years-select--mobile' : ''"
              >
                <template v-slot:prepend>
                  <q-icon name="event" size="xs" color="grey-6" />
                </template>
              </q-select>
            </div>
          </div>
        </div>

        <PlayerStatistics
          :years="selectedOverviewYears"
          :player-counts="playerCountsParam"
        />
      </q-tab-panel>
    </q-tab-panels>
  </q-page>
</template>

<script setup lang="ts">
defineOptions({ name: 'StatisticsPage' });

import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import KennerSelect from 'components/base/KennerSelect.vue';
import KennerPlayerCountFilter from 'components/base/KennerPlayerCountFilter.vue';
import SmoothSwitch from 'components/base/SmoothSwitch.vue';
import LeaderBoard from 'components/season/LeaderBoard.vue';
import PlayerStatistics from 'components/statistics/PlayerStatistics.vue';
import { useUserStore } from 'stores/userStore';
import { useResponsive } from 'src/composables/responsive';
import {
  fetchAvailableYears,
  fetchCurrentSeasonId,
  fetchSeason,
} from 'src/services/seasonService';

const route = useRoute();
const router = useRouter();
const { isMobile } = useResponsive();
const { getAvailableYears } = useUserStore();

type TabType = 'hall-of-fame' | 'records';
const currentTab = ref<TabType>(
  route.query.tab === 'records' ? 'records' : 'hall-of-fame'
);

function onTabChange(newTab: TabType) {
  if (route.query.tab !== newTab) {
    void router.replace({
      query: { ...route.query, tab: newTab },
    });
  }
}

watch(
  () => route.query.tab,
  (tab) => {
    if (tab === 'records' || tab === 'hall-of-fame') {
      currentTab.value = tab;
    }
  }
);

// Tab 1 (Hall of Fame) State
const selectedSeasonYear = ref<number | 'all'>(new Date().getFullYear());
const showAllLeagues = ref(false);
const availableSeasonYears = ref<number[]>([]);

const seasonYearOptions = computed(() => [
  { label: 'All-time', value: 'all' as const },
  ...[...availableSeasonYears.value]
    .sort((a, b) => b - a)
    .map((y) => ({ label: String(y), value: y })),
]);

// Tab 2 (Global Records) State
const selectedOverviewYears = ref<number[]>([]);
const overviewYearOptions = ref<number[]>([]);
const availablePlayerCounts = ['2p', '3p', '4p'];
const selectedPlayerCounts = ref<string[]>(['4p']);

const playerCountsParam = computed(() =>
  selectedPlayerCounts.value.length > 0 ? selectedPlayerCounts.value : undefined
);

onMounted(async () => {
  const [years, currentSeasonId, userYears] = await Promise.all([
    fetchAvailableYears(),
    fetchCurrentSeasonId(),
    getAvailableYears(),
  ]);

  availableSeasonYears.value = years ?? [];
  overviewYearOptions.value = userYears ?? [];

  if (currentSeasonId) {
    const season = await fetchSeason(currentSeasonId);
    if (season) {
      selectedSeasonYear.value = season.year;
    }
  } else if (availableSeasonYears.value.length > 0) {
    selectedSeasonYear.value = availableSeasonYears.value[0];
  }
});
</script>

<style scoped lang="scss">
.page-title-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  background: rgba(99, 102, 241, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  &--mobile {
    width: 32px;
    height: 32px;
    border-radius: 8px;
  }
}

.stats-tabs {
  background: var(--kenner-card-bg);
  border: 1px solid var(--kenner-border-color);
  border-radius: 10px;
  padding: 4px;

  &--mobile {
    padding: 2px;
    min-height: 36px;

    :deep(.q-tab) {
      min-height: 36px;
      padding: 0 8px;
      font-size: 12px;
    }
  }
}

.years-select {
  min-width: 160px;
  max-width: 280px;

  &--mobile {
    min-width: 130px;
    max-width: 180px;
  }
}

.filter-label {
  white-space: nowrap;
}
</style>

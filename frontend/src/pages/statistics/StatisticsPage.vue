<template>
  <q-page class="q-pa-md max-width-container q-mx-auto statistics-page">
    <!-- Header & Filter Bar -->
    <div class="stats-header-bar q-mb-lg">
      <div class="row items-center justify-between q-col-gutter-md">
        <!-- Title and description -->
        <div class="col-12 col-md-auto">
          <div class="row items-center no-wrap">
            <div class="page-title-icon q-mr-sm">
              <q-icon name="query_stats" color="primary" size="24px" />
            </div>
            <div>
              <div class="text-h5 text-weight-bolder text-dark line-height-1">
                Statistics
              </div>
              <div class="text-caption text-grey-6 q-mt-xs">
                Rankings, awards, records &amp; game masteries across seasons
              </div>
            </div>
          </div>
        </div>

        <!-- Filters: Player counts & Years -->
        <div class="col-12 col-md-auto">
          <div class="row items-center q-col-gutter-sm">
            <div class="col-12 col-sm-auto">
              <div class="filter-box row items-center q-gutter-x-xs q-px-sm q-py-xs">
                <q-icon name="groups" size="18px" class="q-mr-xs text-primary" />
                <span class="text-caption text-weight-bold text-grey-8 q-mr-xs">Players:</span>
                <q-chip
                  clickable
                  dense
                  :outline="!isAllPlayerCountsSelected"
                  :color="isAllPlayerCountsSelected ? 'primary' : 'grey-7'"
                  text-color="white"
                  size="sm"
                  class="text-weight-bold"
                  style="border-radius: 4px"
                  @click="toggleAllPlayerCounts"
                >
                  All
                </q-chip>
                <q-chip
                  v-for="pc in availablePlayerCounts"
                  :key="pc"
                  clickable
                  dense
                  :outline="!selectedPlayerCounts.includes(pc)"
                  :color="
                    selectedPlayerCounts.includes(pc) ? 'primary' : 'grey-7'
                  "
                  text-color="white"
                  size="sm"
                  class="text-weight-bold"
                  style="border-radius: 4px"
                  @click="togglePlayerCount(pc)"
                >
                  {{ pc.toUpperCase() }}
                </q-chip>
              </div>
            </div>

            <div class="col-12 col-sm-auto years-filter" style="min-width: 170px">
              <KennerSelect
                v-model="selectedYears"
                :options="yearOptions"
                label="Years"
                multiple
                clearable
                dense
                :display-value="yearsDisplayValue"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <q-tabs
      v-model="currentTab"
      dense
      class="text-grey-7 stats-tabs q-mb-lg"
      active-color="primary"
      indicator-color="primary"
      align="left"
      narrow-indicator
    >
      <q-tab name="players" icon="groups" label="Players & Awards" />
      <q-tab name="games" icon="sports_esports" label="Games & Leaderboards" />
    </q-tabs>

    <!-- Tab Panels -->
    <q-tab-panels
      v-model="currentTab"
      animated
      class="bg-transparent stats-tab-panels"
    >
      <q-tab-panel name="players" class="q-pa-none">
        <PlayerStatistics
          :years="selectedYears"
          :player-counts="playerCountsParam"
        />
      </q-tab-panel>

      <q-tab-panel name="games" class="q-pa-none">
        <GameStatistics
          :years="selectedYears"
          :player-counts="playerCountsParam"
        />
      </q-tab-panel>
    </q-tab-panels>
  </q-page>
</template>

<script setup lang="ts">
defineOptions({ name: 'StatisticsPage' });

import { computed, onMounted, ref } from 'vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import GameStatistics from 'components/statistics/GameStatistics.vue';
import PlayerStatistics from 'components/statistics/PlayerStatistics.vue';
import { useUserStore } from 'stores/userStore';

const { getAvailableYears } = useUserStore();

const currentTab = ref<'players' | 'games'>('players');

const selectedYears = ref<number[]>([]);
const yearOptions = ref<number[]>([]);
const yearsDisplayValue = computed(() =>
  selectedYears.value.length === 0
    ? 'All Time'
    : selectedYears.value
        .slice()
        .sort((a, b) => b - a)
        .join(', ')
);

// Player-count filter, mirroring UsersListPage: default to 4P, empty means
// "All". A backend-friendly value (undefined when All) is derived below.
const availablePlayerCounts = ['2p', '3p', '4p'];
const selectedPlayerCounts = ref<string[]>(['4p']);
const isAllPlayerCountsSelected = computed(
  () => selectedPlayerCounts.value.length === 0
);
const playerCountsParam = computed(() =>
  selectedPlayerCounts.value.length > 0 ? selectedPlayerCounts.value : undefined
);

function togglePlayerCount(val: string) {
  const idx = selectedPlayerCounts.value.indexOf(val);
  if (idx >= 0) {
    selectedPlayerCounts.value.splice(idx, 1);
  } else {
    selectedPlayerCounts.value.push(val);
  }
  // If every individual count is selected, collapse to "All" (empty array).
  if (selectedPlayerCounts.value.length === availablePlayerCounts.length) {
    selectedPlayerCounts.value = [];
  }
}

function toggleAllPlayerCounts() {
  selectedPlayerCounts.value = [];
}

onMounted(async () => {
  const years = await getAvailableYears();
  yearOptions.value = years ?? [];
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
}

.filter-box {
  background: var(--kenner-card-bg);
  border: 1px solid var(--kenner-border-color);
  border-radius: 8px;
  min-height: 40px;
}

.stats-tabs {
  background: var(--kenner-card-bg);
  border: 1px solid var(--kenner-border-color);
  border-radius: 10px;
  padding: 4px;
}

@media (max-width: 599px) {
  .years-filter {
    margin-top: 8px;
  }
}
</style>

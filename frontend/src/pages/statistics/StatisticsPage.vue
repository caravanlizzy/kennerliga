<template>
  <q-page class="q-pa-md max-width-container q-mx-auto statistics-page">
    <div class="q-mb-md">
      <!-- Full width and stacked on mobile so the chips/select never wrap
           into each other; inline once there's room (col-sm-auto). -->
      <div class="row q-col-gutter-sm items-center filters-row">
        <div class="col-12 col-sm-auto">
          <!-- Player-count filter, mirroring the chips on the players list. -->
          <div class="row items-center q-gutter-x-sm">
            <div class="row items-center text-caption text-weight-bold text-grey-8">
              <q-icon name="groups" size="18px" class="q-mr-xs text-primary" />
              <span>Players:</span>
            </div>
            <div class="row q-gutter-xs items-center">
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
                :color="selectedPlayerCounts.includes(pc) ? 'primary' : 'grey-7'"
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
        </div>

        <div class="col-12 col-sm-auto years-filter" style="min-width: 180px">
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

    <!-- Split layout: the per-game leaderboard pinned top-left so it is
         visible without scrolling past the category cards first, with the
         ranking categories on the right. -->
    <div class="row q-col-gutter-lg">
      <div class="col-12 col-md-5">
        <GameStatistics :years="selectedYears" :player-counts="playerCountsParam" />
      </div>

      <div class="col-12 col-md-7">
        <PlayerStatistics :years="selectedYears" :player-counts="playerCountsParam" />
      </div>
    </div>
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

const selectedYears = ref<number[]>([]);
const yearOptions = ref<number[]>([]);
const yearsDisplayValue = computed(() =>
  selectedYears.value.length === 0
    ? 'All Time'
    : selectedYears.value.slice().sort((a, b) => b - a).join(', ')
);

// Player-count filter, mirroring UsersListPage: default to 4P, empty means
// "All". A backend-friendly value (undefined when All) is derived below.
const availablePlayerCounts = ['2p', '3p', '4p'];
const selectedPlayerCounts = ref<string[]>(['4p']);
const isAllPlayerCountsSelected = computed(() => selectedPlayerCounts.value.length === 0);
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
// KennerSelect's floating label rises above its own box -- once the Years
// filter wraps onto its own line below the player chips (mobile), it needs
// a bit of headroom so the label doesn't sit on top of the chips.
@media (max-width: 599px) {
  .years-filter {
    margin-top: 12px;
  }
}
</style>

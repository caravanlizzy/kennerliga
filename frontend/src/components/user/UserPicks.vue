<template>
  <div class="user-picks-view">
    <!-- Header with Title & Year Filter -->
    <div class="row items-center justify-between q-mb-md">
      <div class="row items-center">
        <q-icon name="push_pin" color="primary" size="24px" class="q-mr-sm" />
        <div>
          <div class="text-h5 text-weight-bolder text-heading tracking-tighter">
            Game Picks
          </div>
          <div class="text-caption text-grey-6 text-weight-medium">
            <template v-if="selectedYear === 'all'">
              {{ pickedGames.length }} distinct games picked all-time
            </template>
            <template v-else>
              {{ totalPicksCount }} picks recorded in {{ selectedYear }}
            </template>
          </div>
        </div>
      </div>

      <div class="row items-center q-gutter-x-sm">
        <q-select
          :model-value="selectedYear"
          :options="yearOptions"
          dense
          outlined
          emit-value
          map-options
          options-dense
          class="year-filter-select"
          bg-color="surface-card"
          @update:model-value="$emit('update:selectedYear', $event)"
        >
          <template #prepend>
            <q-icon name="calendar_today" size="xs" color="grey-6" />
          </template>
        </q-select>

        <q-btn flat round dense icon="help_outline" size="sm" color="grey-6">
          <KennerTooltip>
            In Kennerliga, a player can pick the same game at most
            <strong>{{ maxGameLimit }}</strong> times per year.
          </KennerTooltip>
        </q-btn>
      </div>
    </div>

    <!-- Info banner / limit status -->
    <q-banner dense rounded class="q-mb-md surface-banner text-body2">
      <template #avatar>
        <q-icon
          :name="selectedYear === 'all' ? 'history' : 'info'"
          :color="selectedYear === 'all' ? 'teal-7' : 'primary'"
          size="sm"
        />
      </template>
      <div class="row items-center justify-between wrap q-gutter-xs">
        <div>
          <span v-if="selectedYear === 'all'" class="text-weight-bold">
            All-Time Picks Catalog:
          </span>
          <span v-else class="text-weight-bold">
            Season {{ selectedYear }} Picks:
          </span>
          <span class="text-grey-7 q-ml-xs">
            {{
              selectedYear === 'all'
                ? 'Showing all games picked by this player across all seasons.'
                : `Maximum ${maxGameLimit} picks per game allowed per season.`
            }}
          </span>
        </div>
        <q-badge
          :color="selectedYear === 'all' ? 'teal-1' : 'blue-1'"
          :text-color="selectedYear === 'all' ? 'teal-9' : 'primary'"
          class="text-weight-bolder q-px-sm"
        >
          {{ totalPicksCount }} Total Picks
        </q-badge>
      </div>
    </q-banner>

    <!-- Picks Grid -->
    <div v-if="pickedGames.length > 0" class="row q-col-gutter-md">
      <div
        v-for="game in pickedGames"
        :key="game.name + (game.platform || '')"
        class="col-12 col-sm-6"
      >
        <q-card flat bordered class="surface-card pick-card transition-all">
          <q-card-section class="row items-center no-wrap q-py-md q-px-md">
            <q-avatar
              size="40px"
              color="primary"
              text-color="white"
              icon="sports_esports"
              class="shadow-1 q-mr-md flex-shrink-0"
            />
            <div class="col ellipsis q-pr-sm">
              <div
                class="text-subtitle1 text-weight-bold text-heading ellipsis"
              >
                {{ game.name }}
              </div>
              <div class="row items-center q-gutter-x-xs q-mt-xs">
                <q-badge
                  v-if="game.platform"
                  color="grey-3"
                  text-color="grey-8"
                  class="text-weight-bold text-caption platform-badge"
                >
                  {{ game.platform }}
                </q-badge>
              </div>
            </div>

            <!-- Pick Count Badge -->
            <div class="col-auto">
              <template v-if="selectedYear !== 'all'">
                <q-badge
                  :color="game.limit_exceeded ? 'negative' : 'primary'"
                  :outline="!game.limit_exceeded"
                  class="text-weight-bolder pick-count-badge"
                >
                  {{ game.count }} / {{ maxGameLimit }}
                  <KennerTooltip v-if="game.limit_exceeded">
                    Annual pick limit reached ({{ game.count }} /
                    {{ maxGameLimit }})
                  </KennerTooltip>
                </q-badge>
              </template>
              <template v-else>
                <q-badge
                  color="teal-1"
                  text-color="teal-9"
                  class="text-weight-bolder pick-count-badge"
                >
                  {{ game.count }} {{ game.count === 1 ? 'pick' : 'picks' }}
                </q-badge>
              </template>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Empty State -->
    <q-card v-else flat bordered class="surface-card q-pa-xl text-center">
      <q-icon
        name="history_toggle_off"
        size="56px"
        class="q-mb-md text-grey-5"
      />
      <div class="text-h6 text-weight-bold text-heading q-mb-xs">
        No picks recorded
      </div>
      <div class="text-caption text-grey-6">
        {{
          selectedYear === 'all'
            ? 'This player has not picked any games yet.'
            : `No game picks found for season ${selectedYear}.`
        }}
      </div>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import type { TPlayerPickedGame } from 'src/types';

const props = defineProps<{
  pickedGames: TPlayerPickedGame[];
  maxGameLimit: number;
  selectedYear: number | string;
  availableYears: number[];
}>();

defineEmits<{
  (e: 'update:selectedYear', value: number | string): void;
}>();

const yearOptions = computed(() => {
  const options: { label: string; value: number | string }[] = [
    { label: 'All Time', value: 'all' },
  ];
  for (const year of props.availableYears) {
    options.push({ label: String(year), value: year });
  }
  return options;
});

const totalPicksCount = computed(() => {
  return props.pickedGames.reduce((acc, curr) => acc + (curr.count || 1), 0);
});
</script>

<style scoped lang="scss">
.tracking-tighter {
  letter-spacing: -1px;
}

.surface-card {
  background: var(--surface-bg) !important;
  border-color: var(--surface-border) !important;
  border-radius: 12px;
  box-shadow: var(--surface-shadow);
}

.surface-banner {
  background: var(--kenner-surface-subtle) !important;
  border: 1px solid var(--surface-border);
  border-radius: 10px;
}

.pick-card {
  border-radius: 12px;
  &:hover {
    border-color: var(--surface-border-strong) !important;
    background: var(--kenner-surface-subtle) !important;
  }
}

.year-filter-select {
  min-width: 140px;
  :deep(.q-field__control) {
    border-radius: 10px;
    height: 38px;
  }
}

.platform-badge {
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 4px;
}

.pick-count-badge {
  font-size: 0.8rem;
  padding: 4px 10px;
  border-radius: 8px;
}

.text-heading {
  color: var(--text-heading) !important;
}

.flex-shrink-0 {
  flex-shrink: 0;
}

.transition-all {
  transition: all 0.2s ease;
}
</style>

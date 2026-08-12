<template>
  <q-card flat bordered class="rounded-borders overflow-hidden surface-card">
    <q-card-section class="surface-card-header text-weight-bold text-uppercase letter-spacing-1 q-py-sm row items-center justify-between">
      <div class="row items-center q-gutter-x-sm">
        <q-icon name="insights" size="xs" />
        <div class="text-caption text-weight-bolder">Performance</div>
      </div>
      <div class="text-caption text-weight-bold opacity-60">{{ overallStats.total_games }} Games Total</div>
    </q-card-section>
    <q-card-section class="q-pa-md">
      <div class="row q-col-gutter-md q-mb-lg">
        <div class="col-6">
          <q-card flat bordered class="column items-center q-pa-md stat-tile">
            <div class="text-h4 text-weight-bolder text-positive">{{ (overallStats.wins / (overallStats.total_games || 1) * 100).toFixed(0) }}<span class="text-caption text-weight-medium">%</span></div>
            <div class="text-caption text-grey-6 text-uppercase text-weight-bolder letter-spacing-1 q-mt-xs">Win Rate</div>
          </q-card>
        </div>
        <div class="col-6">
          <q-card flat bordered class="column items-center q-pa-md stat-tile">
            <div class="text-h4 text-weight-bolder text-primary">#{{ (overallStats.avg_pos || 0).toFixed(1) }}</div>
            <div class="text-caption text-grey-6 text-uppercase text-weight-bolder letter-spacing-1 q-mt-xs">Avg Pos</div>
          </q-card>
        </div>
      </div>

      <div class="text-caption text-uppercase text-weight-bolder text-grey-6 q-mb-sm letter-spacing-1">Rank Distribution</div>
      <div class="column q-gutter-y-xs">
        <div v-for="pos in [1, 2, 3, 4]" :key="pos" class="distribution-row row items-center q-col-gutter-sm q-py-xs">
          <div class="col-2 text-weight-bold text-grey-7">{{ pos }}{{ getOrdinal(pos) }}</div>
          <div class="col">
            <q-linear-progress
              :value="(overallStats.positions[pos] || 0) / (overallStats.total_games || 1)"
              size="8px"
              :color="getPosColor(pos)"
              track-color="grey-2"
              class="rounded-borders"
            />
          </div>
          <div class="col-3 text-right">
            <div class="text-weight-bolder" :class="getPosColorClass(pos)">
              {{ overallStats.positions[pos] || 0 }}
            </div>
          </div>
        </div>
      </div>

      <q-separator class="q-my-md opacity-50" />
      <div class="row items-center justify-between">
        <div class="text-caption text-grey-7 text-weight-bold">Podiums</div>
        <div class="row q-gutter-x-xs">
          <q-badge v-for="i in 3" :key="i" :color="getPosColor(i)" rounded class="q-px-xs">
            {{ overallStats.positions[i] || 0 }}
          </q-badge>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
defineProps<{
  overallStats: {
    total_games: number;
    wins: number;
    podiums: number;
    avg_pos: number;
    positions: Record<number, number>;
  };
}>();

function getOrdinal(n: number) {
  const s = ['th', 'st', 'nd', 'rd'];
  const v = n % 100;
  return s[(v - 20) % 10] || s[v] || s[0];
}

function getPosColor(pos: number) {
  switch (pos) {
    case 1: return 'amber-8';
    case 2: return 'blue-grey-4';
    case 3: return 'orange-9';
    case 4: return 'brown-5';
    default: return 'grey-6';
  }
}

function getPosColorClass(pos: number) {
  return `text-${getPosColor(pos)}`;
}
</script>

<style scoped lang="scss">
.surface-card {
  background: var(--surface-bg) !important;
  border-color: var(--surface-border) !important;
  border-radius: 12px;
  transition: border-color 0.2s ease;

  &:hover {
    border-color: var(--surface-border-strong) !important;
  }
}

.surface-card-header {
  background: var(--surface-header-bg);
  color: var(--surface-header-text);
  border-bottom: 1px solid var(--divider);
}

.stat-tile {
  background: var(--stat-tile-bg, #f8fafc);
  border: 1px solid var(--surface-border) !important;
  border-radius: 16px;
  transition: all 0.3s ease;

  &:hover {
    border-color: var(--q-primary) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  }
}

.distribution-row {
  transition: background 0.2s ease;
  border-radius: 4px;
  padding: 2px 4px;
  &:hover {
    background: var(--divider);
  }
}

.letter-spacing-1 { letter-spacing: 1px; }
</style>

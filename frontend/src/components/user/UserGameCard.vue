<template>
  <q-card flat bordered class="game-stat-card">
    <q-card-section class="q-pa-md">
      <!-- Title & Plays Count -->
      <div class="row items-center justify-between no-wrap q-mb-sm">
        <div class="text-subtitle1 text-weight-bolder text-heading ellipsis q-pr-sm">
          {{ game.name }}
        </div>
        <q-badge color="grey-2" text-color="grey-7" class="text-weight-bolder plays-badge px-sm">
          {{ game.count }} plays
        </q-badge>
      </div>

      <!-- Metrics & Recent results row -->
      <div class="row items-center no-wrap metrics-container q-pa-sm">
        <!-- Win Rate -->
        <div class="col-auto q-px-md text-center border-right">
          <div class="text-h6 text-weight-bolder text-positive stats-value">
            {{ game.winRate.toFixed(0) }}<span class="text-caption text-weight-medium">%</span>
          </div>
          <div class="text-caption text-grey-6 text-weight-bolder stats-label">WIN</div>
        </div>

        <!-- Avg Pos -->
        <div class="col-auto q-px-md text-center border-right">
          <div class="text-h6 text-weight-bolder text-primary stats-value">
            #{{ game.avgPos.toFixed(1) }}
          </div>
          <div class="text-caption text-grey-6 text-weight-bolder stats-label">AVG</div>
        </div>

        <!-- Last 5 -->
        <div class="col q-pl-md">
          <div class="row q-gutter-x-xs no-wrap justify-end q-mb-xs">
            <div
              v-for="(p, idx) in game.positions.slice(-5).reverse()"
              :key="idx"
              class="mini-result-badge flex flex-center text-weight-bolder"
              :class="[
                `bg-${getPosColor(p)}`,
                p === 1 ? 'text-black' : 'text-white'
              ]"
            >
              {{ p }}
            </div>
          </div>
          <div class="text-right">
            <div class="text-caption text-grey-6 text-weight-bolder stats-label">LAST 5</div>
          </div>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
defineProps<{
  game: {
    name: string;
    winRate: number;
    avgPos: number;
    count: number;
    positions: number[];
  };
}>();

function getPosColor(pos: number) {
  switch (pos) {
    case 1: return 'amber-8';
    case 2: return 'blue-grey-4';
    case 3: return 'orange-9';
    case 4: return 'brown-5';
    default: return 'grey-6';
  }
}
</script>

<style scoped lang="scss">
.game-stat-card {
  position: relative;
  border-radius: 12px;
  background: var(--surface-bg) !important;
  border: 1px solid var(--surface-border) !important;
  overflow: hidden;
}

.plays-badge {
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 4px;
}

.metrics-container {
  border-radius: 10px;
  background: #f8fafc;
  border: 1px solid var(--surface-border);
}

.border-right {
  border-right: 1px solid rgba(0, 0, 0, 0.05);
}

.stats-value {
  line-height: 1.1;
}

.stats-label {
  font-size: 0.6rem;
  letter-spacing: 0.02em;
  margin-top: 2px;
}

.mini-result-badge {
  width: 18px;
  height: 18px;
  font-size: 0.7rem;
  border-radius: 4px;
}


.text-heading { color: var(--text-heading) !important; }
</style>

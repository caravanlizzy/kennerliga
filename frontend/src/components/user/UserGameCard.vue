<template>
  <q-card flat bordered class="game-stat-card">
    <q-card-section class="q-pa-md">
      <!-- Title & Plays Count -->
      <div class="row items-center justify-between no-wrap q-mb-sm">
        <div
          class="text-subtitle1 text-weight-bolder text-heading ellipsis q-pr-sm"
        >
          {{ game.name }}
        </div>
        <div class="row items-center q-gutter-x-xs no-wrap">
          <q-badge
            v-if="recordScore != null"
            color="deep-orange-1"
            text-color="deep-orange-9"
            class="text-weight-bolder plays-badge"
          >
            <q-icon name="local_fire_department" size="10px" class="q-mr-xs" />
            {{ recordScore }} VP
            <KennerTooltip
              >Player holds record ({{ recordScore }} VP)</KennerTooltip
            >
          </q-badge>
          <q-badge
            color="grey-2"
            text-color="grey-7"
            class="text-weight-bolder plays-badge px-sm"
            :class="{ 'cursor-pointer plays-badge--clickable': isClickable }"
            @click="onPlaysClick"
          >
            {{ game.count }} plays
            <KennerTooltip v-if="isClickable">
              View {{ profileName ? `${profileName}'s` : 'all' }} plays
            </KennerTooltip>
          </q-badge>
        </div>
      </div>

      <!-- Metrics & Recent results row -->
      <div class="row items-center no-wrap metrics-container q-pa-sm">
        <!-- Win Rate -->
        <div class="col-auto q-px-md text-center border-right">
          <div class="text-h6 text-weight-bolder text-positive stats-value">
            {{ game.winRate.toFixed(0)
            }}<span class="text-caption text-weight-medium">%</span>
          </div>
          <div class="text-caption text-grey-6 text-weight-bolder stats-label">
            WIN
          </div>
        </div>

        <!-- Avg Pos -->
        <div class="col-auto q-px-md text-center border-right">
          <div class="text-h6 text-weight-bolder text-primary stats-value">
            #{{ game.avgPos.toFixed(1) }}
          </div>
          <div class="text-caption text-grey-6 text-weight-bolder stats-label">
            AVG
          </div>
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
                p === 1 ? 'mini-result-badge--dark-text' : 'text-white',
              ]"
            >
              {{ p }}
            </div>
          </div>
          <div class="text-right">
            <div
              class="text-caption text-grey-6 text-weight-bolder stats-label"
            >
              LAST 5
            </div>
          </div>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import KennerTooltip from 'components/base/KennerTooltip.vue';

const router = useRouter();

const props = defineProps<{
  game: {
    id?: number;
    game_id?: number;
    name: string;
    winRate: number;
    avgPos: number;
    count: number;
    positions: number[];
  };
  recordScore?: number;
  profileId?: number | null;
  profileName?: string;
}>();

const targetGameId = computed(() => props.game.id ?? props.game.game_id);
const isClickable = computed(() => targetGameId.value != null);

function onPlaysClick(e: Event) {
  if (!targetGameId.value) return;
  e.stopPropagation();

  const query: Record<string, string> = {
    tab: 'matches',
  };
  if (props.profileId != null) {
    query.player = String(props.profileId);
  } else if (props.profileName) {
    query.player = props.profileName;
  }

  void router.push({
    name: 'game-detail',
    params: { id: targetGameId.value },
    query,
  });
}

function getPosColor(pos: number) {
  switch (pos) {
    case 1:
      return 'amber-8';
    case 2:
      return 'blue-grey-4';
    case 3:
      return 'orange-9';
    case 4:
      return 'brown-5';
    default:
      return 'grey-6';
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
  transition: all 0.15s ease-in-out;

  &--clickable {
    cursor: pointer;
    user-select: none;

    &:hover {
      background: var(--kenner-surface-subtle, #e2e8f0) !important;
      color: var(--q-primary) !important;
      transform: scale(1.05);
    }
  }
}

.metrics-container {
  border-radius: 10px;
  background: var(--kenner-surface-subtle);
  border: 1px solid var(--surface-border);
}

.border-right {
  border-right: 1px solid var(--kenner-border-subtle);
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

  // Dark text on the amber badge in both themes (text-black is remapped in dark mode)
  &--dark-text {
    color: #000;
  }
}

.text-heading {
  color: var(--text-heading) !important;
}
</style>

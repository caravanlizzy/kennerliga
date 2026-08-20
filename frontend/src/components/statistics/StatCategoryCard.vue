<template>
  <q-card flat bordered class="stat-card full-height">
    <q-card-section class="q-pb-none">
      <div class="row items-center no-wrap">
        <div class="stat-icon-box q-mr-sm">
          <q-icon :name="icon" color="primary" size="22px" />
        </div>
        <div class="column">
          <div class="text-subtitle1 text-weight-bolder text-dark line-height-1">
            {{ category.label }}
          </div>
          <div class="text-caption text-grey-6">{{ category.description }}</div>
        </div>
      </div>
    </q-card-section>

    <q-card-section class="q-pt-sm">
      <div
        class="me-row row items-center justify-between q-pa-sm q-mb-sm rounded-borders"
        :class="category.me.eligible ? 'me-row--ranked' : 'me-row--unranked'"
      >
        <div class="row items-center no-wrap q-gutter-x-sm">
          <q-avatar size="26px" color="primary" text-color="white" class="text-weight-bold text-caption">
            {{ category.me.rank ?? '-' }}
          </q-avatar>
          <span class="text-weight-bold">You</span>
        </div>
        <div v-if="category.me.eligible" class="text-weight-bolder">
          {{ formatStatValue(category.key, category.unit, category.me.value) }}
        </div>
        <div v-else class="text-caption text-grey-6 text-right">
          <template v-if="category.me.value !== null">
            {{ formatStatValue(category.key, category.unit, category.me.value) }} so far
          </template>
          <template v-else>No data yet</template>
          <div v-if="category.min_games">Need {{ category.min_games }}+ games to rank</div>
        </div>
      </div>

      <div v-if="category.top.length === 0" class="text-caption text-grey-6 q-pa-sm">
        Not enough data to rank players yet.
      </div>

      <template v-else>
        <div class="text-caption text-weight-bold text-grey-7 text-uppercase q-mb-xs">
          Top Players
        </div>
        <div
          v-for="entry in category.top"
          :key="'top-' + entry.profile_id"
          class="rank-row row items-center justify-between"
          :class="{ 'rank-row--me': entry.is_me }"
        >
          <div class="row items-center no-wrap q-gutter-x-sm">
            <span class="rank-badge" :class="medalClass(entry.rank)">{{ entry.rank }}</span>
            <span :class="{ 'text-weight-bolder': entry.is_me }">{{ entry.profile_name }}</span>
          </div>
          <span class="text-weight-bold">
            {{ formatStatValue(category.key, category.unit, entry.value) }}
          </span>
        </div>

        <template v-if="visibleAroundMe.length > 0">
          <!-- When the player's neighbourhood is not adjacent to the top
               list, show a divider that makes the skipped ranks obvious. -->
          <div v-if="hasGap" class="gap-separator row items-center q-my-sm">
            <q-separator class="col" />
            <span class="gap-separator__label text-caption text-grey-6">
              <q-icon name="more_vert" size="14px" />
              {{ gapCount }} more
            </span>
            <q-separator class="col" />
          </div>
          <q-separator v-else class="q-my-sm" />
          <div class="text-caption text-weight-bold text-grey-7 text-uppercase q-mb-xs">
            Around You
          </div>
          <div
            v-for="entry in visibleAroundMe"
            :key="'around-' + entry.profile_id"
            class="rank-row row items-center justify-between"
            :class="{ 'rank-row--me': entry.is_me }"
          >
            <div class="row items-center no-wrap q-gutter-x-sm">
              <span class="rank-badge">{{ entry.rank }}</span>
              <span :class="{ 'text-weight-bolder': entry.is_me }">{{ entry.profile_name }}</span>
            </div>
            <span class="text-weight-bold">
              {{ formatStatValue(category.key, category.unit, entry.value) }}
            </span>
          </div>
        </template>
      </template>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { TStatCategory } from 'src/types';
import { formatStatValue } from 'src/composables/statFormat';

const props = defineProps<{ category: TStatCategory }>();

const ICONS: Record<string, string> = {
  career_performance: 'military_tech',
  win_rate: 'percent',
  avg_position: 'trending_up',
  games_played: 'sports_esports',
};

const icon = computed(() => ICONS[props.category.key] ?? 'insights');

// The "around me" window can overlap the top list (e.g. rank 4 when top_n
// is 5) -- only show entries that aren't already visible above.
const visibleAroundMe = computed(() => {
  const topRanks = new Set(props.category.top.map((entry) => entry.rank));
  return props.category.around_me.filter((entry) => !topRanks.has(entry.rank));
});

// A gap exists when the highest-ranked "around me" row does not directly
// follow the last row already shown in the top list -- i.e. there are
// players in between that neither section displays.
const topLastRank = computed(() => {
  const ranks = props.category.top
    .map((entry) => entry.rank)
    .filter((rank): rank is number => rank !== null);
  return ranks.length > 0 ? Math.max(...ranks) : 0;
});

const aroundFirstRank = computed(() => {
  const ranks = visibleAroundMe.value
    .map((entry) => entry.rank)
    .filter((rank): rank is number => rank !== null);
  return ranks.length > 0 ? Math.min(...ranks) : null;
});

const hasGap = computed(
  () => aroundFirstRank.value !== null && aroundFirstRank.value > topLastRank.value + 1
);

const gapCount = computed(() =>
  aroundFirstRank.value !== null ? aroundFirstRank.value - topLastRank.value - 1 : 0
);

function medalClass(rank: number | null): string {
  if (rank === 1) return 'rank-badge--gold';
  if (rank === 2) return 'rank-badge--silver';
  if (rank === 3) return 'rank-badge--bronze';
  return '';
}
</script>

<style scoped lang="scss">
.stat-icon-box {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(99, 102, 241, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.me-row {
  background: rgba(99, 102, 241, 0.06);
  border: 1px solid rgba(99, 102, 241, 0.15);
}

.me-row--unranked {
  background: rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.rank-row {
  padding: 6px 4px;
  border-radius: 6px;
}

.rank-row--me {
  background: rgba(99, 102, 241, 0.08);
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.06);
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
}

.rank-badge--gold {
  background: #f5c344;
  color: #4a3300;
}

.rank-badge--silver {
  background: #c9ccd1;
  color: #33363b;
}

.rank-badge--bronze {
  background: #d99a63;
  color: #3d2306;
}

.gap-separator {
  gap: 8px;
}

.gap-separator__label {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  white-space: nowrap;
  font-style: italic;
}
</style>

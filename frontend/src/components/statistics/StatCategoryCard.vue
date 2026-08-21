<template>
  <q-card flat bordered class="stat-card full-height">
    <q-card-section class="q-pb-sm">
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

    <q-separator class="q-mx-md" />

    <q-card-section class="q-pt-sm">
      <div v-if="rows.length === 0" class="text-caption text-grey-6 q-pa-sm">
        Not enough data to rank players yet.
      </div>

      <!-- A single continuous ranking: the top players and the requesting
           player's neighbourhood are one list. The player's own row is only
           highlighted (no separate "You" section), and a divider marks any
           ranks skipped between the two ends. -->
      <template v-else>
        <template v-for="row in rows" :key="row.key">
          <div v-if="row.type === 'gap'" class="gap-separator row items-center q-my-sm">
            <q-separator class="col" />
            <span class="gap-separator__label text-caption text-grey-6">
              <q-icon name="more_vert" size="14px" />
              {{ row.count }} more
            </span>
            <q-separator class="col" />
          </div>
          <div
            v-else
            class="rank-row row items-center justify-between"
            :class="{ 'rank-row--me': row.entry.is_me }"
          >
            <div class="row items-center no-wrap q-gutter-x-sm">
              <span class="rank-badge">{{ row.entry.rank }}</span>
              <span :class="{ 'text-weight-bolder': row.entry.is_me }">{{ row.entry.profile_name }}</span>
            </div>
            <span class="row items-center no-wrap q-gutter-x-xs text-weight-bold">
              <template v-if="row.entry.best_level != null">
                <LeagueLevel badge :level="row.entry.best_level" />
                <span>{{ formatStatValue(category.key, category.unit, row.entry.value) }}</span>
              </template>
              <template v-else>
                {{ row.entry.display ?? formatStatValue(category.key, category.unit, row.entry.value) }}
              </template>
            </span>
          </div>
        </template>
      </template>

      <!-- The player has data but not enough to be formally ranked: show
           their standing on its own highlighted row, without a heading. -->
      <div
        v-if="!category.me.eligible"
        class="rank-row rank-row--me row items-center justify-between q-mt-sm"
      >
        <div class="row items-center no-wrap q-gutter-x-sm">
          <span class="rank-badge">{{ category.me.rank ?? '–' }}</span>
          <span class="text-weight-bolder">{{ category.me.profile_name }}</span>
        </div>
        <div class="text-caption text-grey-6 text-right row items-center no-wrap q-gutter-x-xs justify-end">
          <template v-if="category.me.best_level != null">
            <LeagueLevel badge :level="category.me.best_level" />
            <span>{{ formatStatValue(category.key, category.unit, category.me.value) }} so far</span>
          </template>
          <template v-else-if="category.me.display">{{ category.me.display }} so far</template>
          <template v-else-if="category.me.value !== null">
            {{ formatStatValue(category.key, category.unit, category.me.value) }} so far
          </template>
          <template v-else>No data yet</template>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { TStatCategory, TStatEntry } from 'src/types';
import { formatStatValue } from 'src/composables/statFormat';
import LeagueLevel from 'components/season/LeagueLevel.vue';

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

// Flatten the top list and the player's neighbourhood into one ordered
// stream of rows so the template renders a single continuous ranking. A
// `gap` row is inserted only when ranks are skipped between the two ends.
type TRankRow =
  | { type: 'entry'; key: string; entry: TStatEntry }
  | { type: 'gap'; key: string; count: number };

const rows = computed<TRankRow[]>(() => {
  const result: TRankRow[] = props.category.top.map((entry) => ({
    type: 'entry',
    key: 'top-' + entry.profile_id,
    entry,
  }));

  if (visibleAroundMe.value.length > 0) {
    if (hasGap.value) {
      result.push({ type: 'gap', key: 'gap', count: gapCount.value });
    }
    for (const entry of visibleAroundMe.value) {
      result.push({ type: 'entry', key: 'around-' + entry.profile_id, entry });
    }
  }

  return result;
});
</script>

<style scoped lang="scss">
.stat-card {
  transition: border-color 0.15s ease;

  &:hover {
    border-color: rgba(99, 102, 241, 0.3);
  }
}

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

.rank-row {
  padding: 6px 4px;
  border-radius: 6px;
  transition: background-color 0.15s ease;

  &:hover {
    background: rgba(0, 0, 0, 0.03);
  }
}

.rank-row--me {
  background: rgba(99, 102, 241, 0.08);

  &:hover {
    background: rgba(99, 102, 241, 0.12);
  }
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

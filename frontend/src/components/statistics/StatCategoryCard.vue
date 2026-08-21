<template>
  <q-card flat bordered class="stat-card full-height">
    <q-card-section class="q-pb-sm">
      <div class="row items-center no-wrap">
        <div class="stat-icon-box q-mr-sm" :style="{ background: accentColor + '14' }">
          <q-icon :name="icon" :style="{ color: accentColor }" size="22px" />
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
      <div v-if="top3.length === 0" class="text-caption text-grey-6 q-pa-sm">
        Not enough data to rank players yet.
      </div>

      <template v-else>
        <!-- Top 3, as small boxes -- mirrors the award podium cards. -->
        <div class="row q-col-gutter-sm">
          <div v-for="(entry, idx) in top3" :key="entry.profile_id" class="col">
            <div class="podium-player" :class="{ 'podium-player--me': entry.is_me }">
              <span class="rank-badge">{{ idx + 1 }}</span>
              <div
                class="podium-player__name ellipsis"
                :class="{ 'text-weight-bolder text-primary': entry.is_me }"
              >
                {{ entry.profile_name }}
              </div>
              <div class="podium-player__score" :style="{ color: accentColor }">
                <template v-if="entry.best_level != null">
                  <LeagueLevel badge :level="entry.best_level" />
                  <div>{{ formatStatValue(category.key, category.unit, entry.value) }}</div>
                </template>
                <template v-else>
                  {{ entry.display ?? formatStatValue(category.key, category.unit, entry.value) }}
                </template>
              </div>
            </div>
          </div>
        </div>

        <!-- Collapsed: a short list around the requesting player (one rank
             above/below). Expanded: every remaining ranked player. -->
        <div v-if="displayedRows.length > 0" class="q-mt-md">
          <div v-if="!expanded && hasGap" class="gap-separator row items-center q-mb-sm">
            <q-separator class="col" />
            <span class="gap-separator__label text-caption text-grey-6">
              <q-icon name="more_vert" size="14px" />
              {{ gapCount }} more
            </span>
            <q-separator class="col" />
          </div>

          <div :class="{ 'full-list': expanded }">
            <template v-for="entry in displayedRows" :key="entry.profile_id">
              <div
                class="rank-row row items-center justify-between"
                :class="{ 'rank-row--me': entry.is_me }"
              >
                <div class="row items-center no-wrap q-gutter-x-sm">
                  <span class="rank-badge">{{ entry.rank }}</span>
                  <span :class="{ 'text-weight-bolder': entry.is_me }">{{ entry.profile_name }}</span>
                </div>
                <span
                  class="row items-center no-wrap q-gutter-x-xs rank-row__value"
                  :style="{ color: accentColor }"
                >
                  <template v-if="entry.best_level != null">
                    <LeagueLevel badge :level="entry.best_level" />
                    <span>{{ formatStatValue(category.key, category.unit, entry.value) }}</span>
                  </template>
                  <template v-else>
                    {{ entry.display ?? formatStatValue(category.key, category.unit, entry.value) }}
                  </template>
                </span>
              </div>
            </template>
          </div>
        </div>

        <div v-if="canExpand" class="text-center q-mt-sm">
          <KennerButton
            flat
            dense
            no-caps
            size="sm"
            color="primary"
            :icon="expanded ? 'expand_less' : 'expand_more'"
            :label="expanded ? 'Show less' : `Show all ${totalRankedLabel}`"
            @click="expanded = !expanded"
          />
        </div>
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
import { computed, ref } from 'vue';
import { TStatCategory } from 'src/types';
import { formatStatValue } from 'src/composables/statFormat';
import LeagueLevel from 'components/season/LeagueLevel.vue';
import KennerButton from 'components/base/KennerButton.vue';

const props = defineProps<{ category: TStatCategory }>();

const expanded = ref(false);

const ICONS: Record<string, string> = {
  career_performance: 'military_tech',
  win_rate: 'percent',
  avg_position: 'trending_up',
  games_played: 'sports_esports',
  hater: 'thumb_down',
  inspirer: 'auto_awesome',
};

// The ranked categories all share the app's plain indigo accent; the "fun"
// superlative awards (Hater, Inspirer) get their own, matching the app's
// existing negative/accent palette (quasar.variables.scss).
const ACCENT_COLORS: Record<string, string> = {
  hater: '#d63a38',
  inspirer: '#5e35b1',
};
const DEFAULT_ACCENT_COLOR = '#4338ca';

const icon = computed(() => ICONS[props.category.key] ?? 'insights');
const accentColor = computed(() => ACCENT_COLORS[props.category.key] ?? DEFAULT_ACCENT_COLOR);

// Only the top 3 are shown as boxes -- mirrors the award podium cards.
const top3 = computed(() => props.category.top.slice(0, 3));

// The "around me" window (one rank above/below) can overlap the top 3
// (e.g. the requesting player is already ranked 2nd) -- only show entries
// that aren't already visible above.
const visibleAroundMe = computed(() => {
  const topRanks = new Set(top3.value.map((entry) => entry.rank));
  return props.category.around_me.filter((entry) => !topRanks.has(entry.rank));
});

// A gap exists when the highest-ranked "around me" row does not directly
// follow the top 3 -- i.e. there are players in between that neither
// section displays.
const topLastRank = computed(() => {
  const ranks = top3.value
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

// Everyone below the top 3 -- the "show all" expansion just reveals the
// rest of what the backend already returned (fetched with a generous
// top_n), no extra request needed.
const restOfList = computed(() => props.category.top.slice(3));
const canExpand = computed(() => restOfList.value.length > 0);
const totalRankedLabel = computed(() => props.category.total_ranked || props.category.top.length);

const displayedRows = computed(() => (expanded.value ? restOfList.value : visibleAroundMe.value));
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

.podium-player {
  height: 100%;
  text-align: center;
  padding: 10px 6px 8px;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: border-color 0.15s ease;

  &:hover {
    border-color: rgba(99, 102, 241, 0.25);
  }

  &--me {
    background: rgba(99, 102, 241, 0.08);
    border-color: rgba(99, 102, 241, 0.2);
  }

  &__name {
    font-size: 12px;
    line-height: 1.2;
    margin-top: 6px;
  }

  &__score {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    font-size: 16px;
    font-weight: 800;
    margin-top: 4px;
    font-variant-numeric: tabular-nums;
  }
}

.rank-row {
  padding: 9px 6px;
  border-radius: 6px;
  transition: background-color 0.15s ease;

  &:hover {
    background: rgba(0, 0, 0, 0.03);
  }
}

.rank-row + .rank-row {
  border-top: 1px solid rgba(0, 0, 0, 0.055);
}

.full-list {
  max-height: 280px;
  overflow-y: auto;
}

.rank-row--me {
  background: rgba(99, 102, 241, 0.08);

  &:hover {
    background: rgba(99, 102, 241, 0.12);
  }
}

.rank-row__value {
  font-weight: 800;
  font-size: 14.5px;
  font-variant-numeric: tabular-nums;
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
  flex-shrink: 0;
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

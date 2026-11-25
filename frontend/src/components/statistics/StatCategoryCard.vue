<template>
  <q-card
    flat
    bordered
    class="stat-card full-height"
    :style="{ '--accent': accentColor }"
  >
    <!-- Header -->
    <q-card-section class="stat-card__header">
      <div class="row items-center justify-between no-wrap">
        <div class="row items-center no-wrap min-width-0">
          <div
            class="stat-icon-box q-mr-sm"
            :style="{
              background: accentColor + ($q.dark.isActive ? '29' : '14'),
            }"
          >
            <q-icon :name="icon" :style="{ color: accentColor }" size="18px" />
          </div>
          <div class="column min-width-0">
            <div
              class="text-subtitle2 text-weight-bolder text-dark line-height-1 ellipsis"
            >
              {{ category.label }}
            </div>
            <div
              class="text-caption text-grey-6 text-ellipsis-2 line-height-1-2 q-mt-xs"
            >
              {{ category.description }}
            </div>
          </div>
        </div>
        <div v-if="category.total_ranked" class="q-ml-xs flex-shrink-0">
          <span class="stat-count-badge">
            {{ category.total_ranked }} ranked
          </span>
        </div>
      </div>
    </q-card-section>

    <q-separator class="stat-card__separator" />

    <!-- Body -->
    <q-card-section class="stat-card__body">
      <div
        v-if="category.top.length === 0"
        class="text-caption text-grey-6 q-pa-sm text-center"
      >
        Not enough data to rank players yet.
      </div>

      <template v-else>
        <!-- Unified Ranking List -->
        <div
          class="stat-rows-container"
          :class="{ 'stat-rows-container--expanded': expanded }"
        >
          <!-- Expanded View: All Ranked Players -->
          <template v-if="expanded">
            <div
              v-for="entry in category.top"
              :key="`exp-${entry.profile_id}`"
              class="stat-rank-row row items-center justify-between no-wrap"
              :class="{
                'stat-rank-row--me': entry.is_me,
                'stat-rank-row--top1': entry.rank === 1,
                'cursor-pointer': Boolean(entry.username),
              }"
              @click="navigateToUser(entry.username)"
            >
              <div class="row items-center no-wrap q-gutter-x-sm min-width-0">
                <span
                  class="rank-badge"
                  :class="
                    entry.rank != null && entry.rank <= 3
                      ? `rank-badge--${entry.rank - 1}`
                      : ''
                  "
                >
                  {{ entry.rank ?? '–' }}
                </span>
                <span
                  class="stat-rank-row__name ellipsis"
                  :class="{
                    'text-weight-bolder': entry.is_me,
                    'player-link': Boolean(entry.username),
                  }"
                >
                  {{ entry.profile_name }}
                </span>
                <span v-if="entry.is_me" class="you-badge">You</span>
              </div>
              <div
                class="stat-rank-row__value row items-center no-wrap q-gutter-x-xs flex-shrink-0"
              >
                <template v-if="entry.best_level != null">
                  <LeagueLevel badge :level="entry.best_level" />
                  <span>{{
                    formatStatValue(category.key, category.unit, entry.value)
                  }}</span>
                </template>
                <template v-else>
                  {{
                    entry.display ??
                    formatStatValue(category.key, category.unit, entry.value)
                  }}
                </template>
              </div>
            </div>
          </template>

          <!-- Collapsed View: Top 3 + Window around user -->
          <template v-else>
            <!-- Top 3 -->
            <div
              v-for="entry in top3"
              :key="`top-${entry.profile_id}`"
              class="stat-rank-row row items-center justify-between no-wrap"
              :class="{
                'stat-rank-row--me': entry.is_me,
                'stat-rank-row--top1': entry.rank === 1,
                'cursor-pointer': Boolean(entry.username),
              }"
              @click="navigateToUser(entry.username)"
            >
              <div class="row items-center no-wrap q-gutter-x-sm min-width-0">
                <span
                  class="rank-badge"
                  :class="
                    entry.rank != null && entry.rank <= 3
                      ? `rank-badge--${entry.rank - 1}`
                      : ''
                  "
                >
                  {{ entry.rank ?? '–' }}
                </span>
                <span
                  class="stat-rank-row__name ellipsis"
                  :class="{
                    'text-weight-bolder': entry.is_me,
                    'player-link': Boolean(entry.username),
                  }"
                >
                  {{ entry.profile_name }}
                </span>
                <span v-if="entry.is_me" class="you-badge">You</span>
              </div>
              <div
                class="stat-rank-row__value row items-center no-wrap q-gutter-x-xs flex-shrink-0"
              >
                <template v-if="entry.best_level != null">
                  <LeagueLevel badge :level="entry.best_level" />
                  <span>{{
                    formatStatValue(category.key, category.unit, entry.value)
                  }}</span>
                </template>
                <template v-else>
                  {{
                    entry.display ??
                    formatStatValue(category.key, category.unit, entry.value)
                  }}
                </template>
              </div>
            </div>

            <!-- Gap Separator (if user's window is further down) -->
            <div
              v-if="!isMeInTop3 && visibleAroundMe.length > 0 && hasGap"
              class="stat-gap-row row items-center justify-center q-my-xs"
            >
              <div class="stat-gap-line col" />
              <span class="stat-gap-text text-caption text-grey-6 q-px-sm">
                &middot;&middot;&middot; {{ gapCount }}
                {{
                  gapCount === 1 ? 'player' : 'players'
                }}
                &middot;&middot;&middot;
              </span>
              <div class="stat-gap-line col" />
            </div>

            <!-- Around Me Rows (if outside top 3) -->
            <template v-if="!isMeInTop3 && visibleAroundMe.length > 0">
              <div
                v-for="entry in visibleAroundMe"
                :key="`around-${entry.profile_id}`"
                class="stat-rank-row row items-center justify-between no-wrap"
                :class="{
                  'stat-rank-row--me': entry.is_me,
                  'cursor-pointer': Boolean(entry.username),
                }"
                @click="navigateToUser(entry.username)"
              >
                <div class="row items-center no-wrap q-gutter-x-sm min-width-0">
                  <span class="rank-badge">{{ entry.rank }}</span>
                  <span
                    class="stat-rank-row__name ellipsis"
                    :class="{
                      'text-weight-bolder': entry.is_me,
                      'player-link': Boolean(entry.username),
                    }"
                  >
                    {{ entry.profile_name }}
                  </span>
                  <span v-if="entry.is_me" class="you-badge">You</span>
                </div>
                <div
                  class="stat-rank-row__value row items-center no-wrap q-gutter-x-xs flex-shrink-0"
                >
                  <template v-if="entry.best_level != null">
                    <LeagueLevel badge :level="entry.best_level" />
                    <span>{{
                      formatStatValue(category.key, category.unit, entry.value)
                    }}</span>
                  </template>
                  <template v-else>
                    {{
                      entry.display ??
                      formatStatValue(category.key, category.unit, entry.value)
                    }}
                  </template>
                </div>
              </div>
            </template>
          </template>
        </div>

        <!-- Ineligible / Unranked Player Notice -->
        <div
          v-if="!category.me.eligible && category.me.profile_name"
          class="stat-rank-row stat-rank-row--me stat-rank-row--unranked row items-center justify-between no-wrap q-mt-xs"
        >
          <div class="row items-center no-wrap q-gutter-x-sm min-width-0">
            <span class="rank-badge rank-badge--unranked">&ndash;</span>
            <span class="stat-rank-row__name ellipsis text-weight-bolder">
              {{ category.me.profile_name }}
            </span>
            <span class="you-badge">You</span>
          </div>
          <div
            class="stat-rank-row__value text-caption text-grey-6 text-right flex-shrink-0"
          >
            <template v-if="category.me.best_level != null">
              <LeagueLevel badge :level="category.me.best_level" />
              <span
                >{{
                  formatStatValue(
                    category.key,
                    category.unit,
                    category.me.value
                  )
                }}
                so far</span
              >
            </template>
            <template v-else-if="category.me.display">
              {{ category.me.display }} so far
            </template>
            <template v-else-if="category.me.value !== null">
              {{
                formatStatValue(category.key, category.unit, category.me.value)
              }}
              so far
            </template>
            <template v-else> No data yet </template>
          </div>
        </div>

        <!-- Show All Toggle Button -->
        <div v-if="canExpand" class="text-center q-mt-xs">
          <KennerButton
            flat
            dense
            no-caps
            size="sm"
            color="primary"
            :icon="expanded ? 'expand_less' : 'expand_more'"
            :label="expanded ? 'Show top 3' : `Show all ${totalRankedLabel}`"
            class="stat-expand-btn"
            @click="expanded = !expanded"
          />
        </div>
      </template>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { TStatCategory } from 'src/types';
import { formatStatValue } from 'src/composables/statFormat';
import LeagueLevel from 'components/season/LeagueLevel.vue';
import KennerButton from 'components/base/KennerButton.vue';

const props = defineProps<{ category: TStatCategory }>();

const router = useRouter();
const expanded = ref(false);

function navigateToUser(username: string | null) {
  if (username) {
    void router.push({ name: 'user-detail', params: { username } });
  }
}

const ICONS: Record<string, string> = {
  career_performance: 'military_tech',
  win_rate: 'percent',
  avg_position: 'trending_up',
  games_played: 'sports_esports',
  records: 'local_fire_department',
  iron_will: 'shield',
  hater: 'thumb_down',
  inspirer: 'auto_awesome',
  spammer: 'repeat',
};

const ACCENT_COLORS: Record<string, string> = {
  career_performance: '#b45309',
  win_rate: '#0f766e',
  avg_position: '#2563eb',
  games_played: '#059669',
  records: '#ea580c',
  iron_will: '#475569',
  hater: '#dc2626',
  inspirer: '#7c3aed',
  spammer: '#d97706',
};
const DEFAULT_ACCENT_COLOR = '#475569';

const ACCENT_COLORS_DARK: Record<string, string> = {
  career_performance: '#fbbf24',
  win_rate: '#2dd4bf',
  avg_position: '#60a5fa',
  games_played: '#34d399',
  records: '#fb923c',
  iron_will: '#94a3b8',
  hater: '#f87171',
  inspirer: '#a78bfa',
  spammer: '#fbbf24',
};
const DEFAULT_ACCENT_COLOR_DARK = '#cbd5e1';

const $q = useQuasar();

const icon = computed(() => ICONS[props.category.key] ?? 'insights');
const accentColor = computed(() =>
  $q.dark.isActive
    ? ACCENT_COLORS_DARK[props.category.key] ?? DEFAULT_ACCENT_COLOR_DARK
    : ACCENT_COLORS[props.category.key] ?? DEFAULT_ACCENT_COLOR
);

const top3 = computed(() => props.category.top.slice(0, 3));
const isMeInTop3 = computed(() => top3.value.some((entry) => entry.is_me));

const visibleAroundMe = computed(() => {
  const topRanks = new Set(top3.value.map((entry) => entry.rank));
  return props.category.around_me.filter((entry) => !topRanks.has(entry.rank));
});

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
  () =>
    aroundFirstRank.value !== null &&
    aroundFirstRank.value > topLastRank.value + 1
);

const gapCount = computed(() =>
  aroundFirstRank.value !== null
    ? aroundFirstRank.value - topLastRank.value - 1
    : 0
);

const canExpand = computed(() => props.category.top.length > 3);
const totalRankedLabel = computed(
  () => props.category.total_ranked || props.category.top.length
);
</script>

<style scoped lang="scss">
.stat-card {
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.stat-card__header {
  padding: 12px 14px 10px;
}

.stat-card__separator {
  opacity: 0.6;
}

.stat-card__body {
  padding: 8px 10px 10px;
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
}

.stat-icon-box {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-count-badge {
  font-size: 11px;
  font-weight: 600;
  color: var(--kenner-text-secondary);
  background: var(--kenner-surface-subtle);
  border: 1px solid var(--kenner-border-subtle);
  padding: 2px 7px;
  border-radius: 999px;
  white-space: nowrap;
}

.stat-rows-container {
  display: flex;
  flex-direction: column;
  gap: 2px;

  &--expanded {
    max-height: 280px;
    overflow-y: auto;
    padding-right: 2px;
  }
}

.stat-rank-row {
  padding: 5px 8px;
  border-radius: 6px;
  transition: background-color 0.15s ease;
  min-height: 34px;

  &:hover {
    background: var(--kenner-hover-bg);
  }

  &--top1 {
    background: rgba(245, 158, 11, 0.04);

    .body--dark & {
      background: rgba(245, 158, 11, 0.07);
    }
  }

  &--me {
    background: color-mix(in srgb, var(--accent) 10%, white);
    border: 1px solid color-mix(in srgb, var(--accent) 25%, transparent);

    &:hover {
      background: color-mix(in srgb, var(--accent) 15%, white);
    }

    .body--dark & {
      background: color-mix(in srgb, var(--accent) 14%, var(--kenner-card-bg));
      border-color: color-mix(in srgb, var(--accent) 35%, transparent);

      &:hover {
        background: color-mix(
          in srgb,
          var(--accent) 20%,
          var(--kenner-card-bg)
        );
      }
    }
  }

  &--unranked {
    border-style: dashed;
    margin-top: 4px;
  }

  &__name {
    font-size: 13px;
    font-weight: 600;
    line-height: 1.2;
  }

  .player-link:hover {
    text-decoration: underline;
  }

  &__value {
    font-weight: 700;
    font-size: 13px;
    font-variant-numeric: tabular-nums;
    color: var(--kenner-text-strong);
  }
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.06);
  font-size: 11px;
  font-weight: 700;
  color: var(--kenner-text-secondary);
  flex-shrink: 0;

  .body--dark & {
    background: rgba(255, 255, 255, 0.08);
  }

  &--0 {
    background: #fef08a;
    color: #854d0e;

    .body--dark & {
      background: var(--kenner-gold-bg);
      color: var(--kenner-gold-text);
    }
  }

  &--1 {
    background: #e2e8f0;
    color: #475569;

    .body--dark & {
      background: var(--kenner-silver-bg);
      color: var(--kenner-silver-text);
    }
  }

  &--2 {
    background: #fed7aa;
    color: #9a3412;

    .body--dark & {
      background: var(--kenner-bronze-bg);
      color: var(--kenner-bronze-text);
    }
  }

  &--unranked {
    background: transparent;
    color: var(--kenner-text-muted);
  }
}

.you-badge {
  display: inline-flex;
  align-items: center;
  padding: 1px 5px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  background: var(--accent);
  color: #ffffff;
  flex-shrink: 0;

  .body--dark & {
    color: #1e293b;
  }
}

.stat-gap-row {
  margin: 2px 0;
}

.stat-gap-line {
  height: 1px;
  background: var(--kenner-border-subtle);
}

.stat-gap-text {
  font-size: 11px;
  font-style: italic;
  white-space: nowrap;
}

.stat-expand-btn {
  font-weight: 600;
  letter-spacing: 0.1px;
}

.min-width-0 {
  min-width: 0;
}

.text-ellipsis-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

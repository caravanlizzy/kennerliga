<template>
  <q-card v-if="results.length > 0" flat class="match-results-card">
    <q-card-section
      v-if="displayGameName"
      class="q-py-sm q-px-md row items-center bg-grey-1"
    >
      <div class="text-subtitle1 text-weight-bold text-grey-9 ellipsis">
        {{ selectedGame.game_name }}
      </div>
      <q-space />
      <q-badge rounded color="grey-3" text-color="grey-7" class="q-px-sm">
        {{ results.length }} players
      </q-badge>
    </q-card-section>

    <q-separator v-if="displayGameName" />

    <q-list class="q-py-sm">
      <q-item
        v-for="result in results"
        :key="result.id"
        class="match-result-item"
        :class="rowClass(result.position)"
      >
        <!-- Rank / Position -->
        <q-item-section side class="q-pr-sm">
          <div
            class="rank-display column items-center justify-center"
            :class="rankClass(result.position)"
          >
            <span class="text-weight-bolder">{{ result.position ?? '-' }}</span>
          </div>
        </q-item-section>

        <!-- Name + optional note + tie-breaker + Stats -->
        <q-item-section>
          <div class="row items-center full-width no-wrap content-container">
            <div class="player-name-col">
              <div class="row items-center no-wrap">
                <q-icon
                  v-if="result.position != null && result.position <= 3"
                  :name="rankIcon(result.position)"
                  :color="rankColor(result.position)"
                  size="20px"
                  class="q-mr-xs shrink-0 podium-icon"
                />
                <span class="text-subtitle2 text-weight-bold ellipsis name-text">
                  {{ result.profile_name }}
                </span>
              </div>

              <div
                v-if="result.notes || result.decisive_tie_breaker"
                class="text-caption text-grey-6 row items-center q-mt-xs"
              >
                <template v-if="result.notes">
                  <q-icon name="notes" size="14px" class="q-mr-xs" />
                  <span class="ellipsis">{{ result.notes }}</span>
                </template>
                <span
                  v-if="result.notes && result.decisive_tie_breaker"
                  class="q-mx-xs opacity-50"
                  >•</span
                >
                <template v-if="result.decisive_tie_breaker">
                  <q-icon name="balance" size="14px" class="q-mr-xs" />
                  <span class="text-weight-medium text-grey-8">TB:</span>
                  <span class="q-ml-xs text-grey-7">{{ result.decisive_tie_breaker }} ({{ result.tie_breaker_value }})</span>
                </template>
              </div>
            </div>

            <!-- Stats -->
            <div class="stats-col-new row items-center justify-end q-gutter-sm">
              <!-- Win Condition / Option badge -->
              <q-badge
                v-if="shouldShowWinCondition(result)"
                color="indigo-1"
                text-color="indigo-8"
                class="stat-badge elegant-badge"
              >
                <q-icon name="flag_circle" size="14px" class="q-mr-xs" />
                <span class="ellipsis">
                  {{ result.win_condition_option_name || result.win_condition_name }}
                </span>
                <KennerTooltip v-if="result.win_condition_name">
                  <span class="text-weight-bold">Win condition:</span>
                  {{ result.win_condition_name }}<template
                    v-if="result.win_condition_option_name"
                  > — {{ result.win_condition_option_name }}</template>
                </KennerTooltip>
              </q-badge>

              <q-badge
                v-if="result.points != null && selectedGame.has_points !== false"
                :color="result.position === 1 ? 'amber-1' : 'grey-2'"
                :text-color="result.position === 1 ? 'amber-9' : 'grey-8'"
                class="stat-badge elegant-badge"
              >
                <q-icon name="stars" size="14px" class="q-mr-xs" />
                <span class="text-weight-bold">{{ result.points }}</span>
              </q-badge>

              <q-badge
                v-if="result.starting_position"
                color="grey-2"
                text-color="grey-7"
                class="stat-badge elegant-badge"
              >
                <q-icon name="start" size="14px" class="q-mr-xs" />
                {{ result.starting_position }}
              </q-badge>

              <q-badge
                v-if="result.starting_points != null"
                color="blue-grey-1"
                text-color="blue-grey-7"
                class="stat-badge elegant-badge"
              >
                <q-icon name="bolt" size="14px" class="q-mr-xs" />
                {{ result.starting_points }}
              </q-badge>

              <!-- Multiple Factions Displayed by Level -->
              <q-badge
                v-for="faction in result.factions"
                :key="faction.id"
                color="deep-purple-1"
                text-color="deep-purple-8"
                class="stat-badge elegant-badge"
              >
                <q-icon name="shield" size="14px" class="q-mr-xs" />
                <span class="ellipsis max-faction-width">
                  {{ faction.name }}
                </span>
              </q-badge>
            </div>
          </div>
        </q-item-section>
      </q-item>
    </q-list>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useLeagueStore } from 'stores/leagueStore';
import { useUserStore } from 'stores/userStore';
import KennerTooltip from 'components/base/KennerTooltip.vue';

import { TSelectedGameDto, TMatchResultDto } from 'src/types';

const props = withDefaults(
  defineProps<{
    selectedGame: TSelectedGameDto;
    displayGameName: boolean;
    matchResults?: Record<number, TMatchResultDto[]>; // optional
  }>(),
  {
    displayGameName: true,
    matchResults: undefined,
  }
);

const { user } = storeToRefs(useUserStore());

const leagueStore = computed(() => {
  const leagueId = user.value?.myCurrentLeagueId;
  return leagueId != null ? useLeagueStore(leagueId)() : null;
});

const rawResults = computed(() => {
  let src: TMatchResultDto[] = [];

  if (props.matchResults) {
    src = Object.values(props.matchResults)
      .flat()
      .filter((r) => r.selected_game === props.selectedGame.id);
  } else {
    src =
      (leagueStore.value?.matchResultsBySelectedGame?.[
        props.selectedGame.id
      ] as TMatchResultDto[]) ?? [];
  }

  return src.map((r) => ({
    id: r.id,
    profile_name: r.player_profile_name,
    points: r.points ?? null,
    position: r.position ?? null,
    notes: r.notes ?? null,
    starting_position: r.starting_position ?? null,
    starting_points: r.starting_points ?? null,
    tie_breaker_value: r.tie_breaker_value ?? null,
    decisive_tie_breaker: r.decisive_tie_breaker?.name ?? null,
    win_condition_name: r.win_condition?.name ?? null,
    win_condition_option_name: r.win_condition_option?.name ?? null,
    // The API now returns 'factions' as a list of objects with id, faction_name, level
    factions: (r.factions ?? [])
      .slice()
      .sort((a, b) => (a.level ?? 0) - (b.level ?? 0)),
  }));
});

const results = computed(() => {
  const mapped = rawResults.value.slice();

  // Primary sort by position (which handles ties/shared places), secondary by points
  mapped.sort((a, b) => {
    if (a.position != null && b.position != null) {
      return a.position - b.position;
    }
    if (a.points != null && b.points != null) {
      return b.points - a.points;
    }
    return 0;
  });

  return mapped;
});

function shouldShowWinCondition(result: any) {
  const name = result.win_condition_name;
  if (!name) return !!result.win_condition_option_name;
  const lowerName = name.toLowerCase().trim();
  return (
    lowerName !== 'points' &&
    lowerName !== 'victory points' &&
    lowerName !== 'score' &&
    lowerName !== 'point'
  );
}

function rankColor(position: number | null) {
  if (position === 1) return 'amber-7';
  if (position === 2) return 'blue-grey-5';
  if (position === 3) return 'brown-5';
  return 'grey-4';
}

function rankTextColor(position: number | null) {
  return position != null && position <= 3 ? 'white' : 'grey-9';
}

function rankIcon(position: number | null) {
  if (position === 1) return 'emoji_events';
  if (position === 2) return 'workspace_premium';
  return 'military_tech';
}

function rankClass(position: number | null) {
  if (position === 1) return 'rank-1';
  if (position === 2) return 'rank-2';
  if (position === 3) return 'rank-3';
  return '';
}

function rowClass(position: number | null) {
  return {
    'is-first': position === 1,
    'is-podium': position != null && position <= 3,
  };
}
</script>

<style scoped lang="scss">
.match-results-card {
  border-radius: 12px;
  overflow: hidden;
}

.match-result-item {
  padding: 12px 16px;
  border-radius: 10px;
  margin: 4px 12px;
  transition: all 0.2s ease;
  border: 1px solid transparent;

  &:hover {
    background: #f8f9fa;
    border-color: #eee;
  }

  &.is-podium {
    margin-top: 6px;
    margin-bottom: 6px;
  }

  &.is-first {
    background: linear-gradient(
      to right,
      rgba(255, 193, 7, 0.05),
      rgba(255, 193, 7, 0.02)
    );
    border-color: rgba(255, 193, 7, 0.2);

    &:hover {
      background: linear-gradient(
        to right,
        rgba(255, 193, 7, 0.08),
        rgba(255, 193, 7, 0.04)
      );
      border-color: rgba(255, 193, 7, 0.3);
    }
  }
}

.rank-display {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #f1f3f5;
  color: #495057;
  font-size: 0.9rem;

  &.rank-1 {
    background: #fff3bf;
    color: #f08c00;
    border: 1px solid #ffe066;
  }
  &.rank-2 {
    background: #f1f3f5;
    color: #495057;
    border: 1px solid #dee2e6;
  }
  &.rank-3 {
    background: #fff4e6;
    color: #d9480f;
    border: 1px solid #ffd8a8;
  }
}

.podium-icon {
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}

.name-text {
  letter-spacing: -0.01em;
}

.elegant-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 500;
  height: 26px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.content-container {
  gap: 12px;
}

.player-name-col {
  flex: 1 1 120px;
  min-width: 0;
}

.stats-col-new {
  flex: 0 0 auto;
}

.max-faction-width {
  max-width: 100px;
}

.shrink-0 {
  flex-shrink: 0;
}

.opacity-50 {
  opacity: 0.5;
}

@media (max-width: 600px) {
  .content-container {
    flex-wrap: wrap;
    gap: 8px;
  }
  .player-name-col {
    flex-basis: 100%;
  }
  .stats-col-new {
    width: 100%;
    justify-content: flex-start !important;
  }
}
</style>

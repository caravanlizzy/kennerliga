<template>
  <q-card v-if="results.length > 0" flat>
    <q-card-section
      v-if="displayGameName"
      class="q-py-sm q-px-md row items-center"
    >
      <div class="text-subtitle1 text-weight-medium ellipsis">
        {{ selectedGame.game_name }}
      </div>
      <q-space />
      <q-badge outline color="grey-7" class="q-ml-sm">
        {{ results.length }} players
      </q-badge>
    </q-card-section>

    <q-separator v-if="displayGameName" />

    <q-list class="q-py-xs">
      <q-item
        v-for="result in results"
        :key="result.id"
        class="match-result-item"
        :class="rowClass(result.position)"
      >
        <!-- Rank / Position -->
        <q-item-section side class="q-pr-sm">
          <q-avatar
            size="34px"
            :color="rankColor(result.position)"
            :text-color="rankTextColor(result.position)"
            class="rank-avatar"
          >
            <span class="text-weight-bold">{{ result.position ?? '-' }}</span>
          </q-avatar>
        </q-item-section>

        <!-- Name + optional note + tie-breaker -->
        <q-item-section>
          <q-item-label class="row items-center no-wrap">
            <q-icon
              v-if="result.position != null && result.position <= 3"
              :name="rankIcon(result.position)"
              :color="rankColor(result.position)"
              size="18px"
              class="q-mr-xs"
            />
            <span class="text-weight-medium ellipsis">
              {{ result.profile_name }}
            </span>
          </q-item-label>

          <q-item-label
            v-if="result.notes || result.decisive_tie_breaker"
            caption
            class="text-grey-7 ellipsis"
          >
            <template v-if="result.notes">
              <q-icon name="notes" size="14px" class="q-mr-xs" />
              {{ result.notes }}
            </template>
            <span
              v-if="result.notes && result.decisive_tie_breaker"
              class="q-mx-xs"
              >•</span
            >
            <template v-if="result.decisive_tie_breaker">
              <q-icon name="Equalizer" size="14px" class="q-mr-xs" />
              TB: {{ result.decisive_tie_breaker }} ({{
                result.tie_breaker_value
              }})
            </template>
          </q-item-label>
        </q-item-section>

        <!-- Stats -->
        <q-item-section side class="stats-col">
          <div class="row items-center justify-end q-gutter-xs">
            <q-badge
              v-if="result.points != null"
              :color="result.position === 1 ? 'amber-7' : 'grey-6'"
              class="stat-badge"
            >
              <q-icon name="star" size="14px" class="q-mr-xs" />
              {{ result.points }}
            </q-badge>

            <q-badge
              v-if="result.starting_position"
              color="grey-5"
              class="stat-badge"
            >
              <q-icon name="flag" size="14px" class="q-mr-xs" />
              {{ result.starting_position }}
            </q-badge>

            <q-badge
              v-if="result.starting_points != null"
              color="blue-grey-4"
              class="stat-badge"
            >
              <q-icon name="bolt" size="14px" class="q-mr-xs" />
              {{ result.starting_points }}
            </q-badge>

            <!-- Multiple Factions Displayed by Level -->
            <q-badge
              v-for="faction in result.factions"
              :key="faction.id"
              color="indigo-6"
              class="stat-badge"
            >
              <q-icon name="shield" size="14px" class="q-mr-xs" />
              <span class="ellipsis" style="max-width: 120px">
                {{ faction.name }}
              </span>
            </q-badge>
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

const props = withDefaults(
  defineProps<{
    selectedGame: any;
    displayGameName: boolean;
    matchResults?: Record<number, any[]>; // optional
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
  let src: any[] = [];

  if (props.matchResults) {
    src = Object.values(props.matchResults)
      .flat()
      .filter((r: any) => r.selected_game === props.selectedGame.id);
  } else {
    src =
      leagueStore.value?.matchResultsBySelectedGame?.[props.selectedGame.id] ??
      [];
  }

  return src.map((r: any) => ({
    id: r.id,
    profile_name: r.player_profile_name,
    points: r.points ?? null,
    position: r.position ?? null,
    notes: r.notes ?? null,
    starting_position: r.starting_position ?? null,
    starting_points: r.starting_points ?? null,
    tie_breaker_value: r.tie_breaker_value ?? null,
    decisive_tie_breaker: r.decisive_tie_breaker?.name ?? null,
    // The API now returns 'factions' as a list of objects with id, faction_name, level
    factions: (r.factions ?? [])
      .slice()
      .sort((a: any, b: any) => (a.level ?? 0) - (b.level ?? 0)),
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

function rowClass(position: number | null) {
  return {
    'is-first': position === 1,
    'is-podium': position != null && position <= 3,
  };
}
</script>

<style scoped>
.match-result-item {
  padding: 10px 12px;
  border-radius: 8px;
  margin: 6px 8px;
}
.match-result-item.is-first {
  box-shadow: inset 0 0 0 1px rgba(251, 192, 45, 0.45);
  background: rgba(251, 192, 45, 0.08);
}
.rank-avatar {
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
}
.stat-badge {
  padding: 4px 8px;
  border-radius: 999px;
}
</style>

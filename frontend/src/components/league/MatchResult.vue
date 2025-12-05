<template>
  <q-card
    flat
    v-if="results.length > 0"
  >
    <div v-if="displayGameName" class="row items-center justify-center q-mb-xs">
      <div class="text-h6 text-weight-bold q-px-md q-py-sm">
        {{ selectedGame.game_name }}
      </div>
    </div>

    <q-list bordered separator class="rounded-borders">
      <q-item
        v-for="(result, index) in results"
        :key="result.id"
        :class="['q-py-md', index === 0 ? 'bg-amber-1' : '']"
      >
        <!-- Rank Badge -->
        <q-item-section side class="q-pr-md">
          <q-avatar
            :color="index === 0 ? 'amber' : 'grey-4'"
            :text-color="index === 0 ? 'amber-10' : 'grey-8'"
            size="42px"
            :class="index === 0 ? 'shadow-2' : ''"
          >
            <span
              :class="index === 0 ? 'text-weight-bold text-h6' : 'text-body1'"
            >
              {{ index + 1 }}
            </span>
          </q-avatar>
        </q-item-section>

        <!-- Player Name + optional note under it -->
        <q-item-section>
          <q-item-label
            :class="[
              'text-body1',
              index === 0
                ? 'text-weight-bold text-amber-10'
                : 'text-weight-medium',
            ]"
          >
            <q-icon
              v-if="index === 0"
              name="emoji_events"
              color="amber"
              size="20px"
              class="q-mr-xs"
            />
            {{ result.profile_name }}
          </q-item-label>

          <!-- Notes (only if present) -->
          <q-item-label
            v-if="result.notes"
            caption
            class="q-mt-xs text-grey-7"
          >
            <q-icon
              name="notes"
              size="16px"
              class="q-mr-xs"
            />
            {{ result.notes }}
          </q-item-label>
        </q-item-section>

        <!-- Stats -->
        <q-item-section side class="row q-gutter-xs items-center">
          <!-- Points (for points-based games) -->
          <q-chip
            v-if="result.points != null"
            dense
            :color="index === 0 ? 'amber' : 'grey-3'"
            :text-color="index === 0 ? 'amber-10' : 'black'"
            :class="index === 0 ? 'text-weight-bold' : ''"
          >
            <q-icon name="star" size="16px" class="q-mr-xs" />
            {{ result.points }}
          </q-chip>

          <!-- Position (for non-points games, or if you still track it) -->
          <q-chip
            v-if="result.position != null"
            dense
            color="grey-3"
            text-color="grey-8"
            size="sm"
          >
            <q-icon name="looks_one" size="14px" class="q-mr-xs" />
            Pos {{ result.position }}
          </q-chip>

          <!-- Starting Position -->
          <q-chip
            v-if="result.starting_position"
            dense
            color="grey-3"
            text-color="grey-8"
            size="sm"
          >
            <q-icon name="flag" size="14px" class="q-mr-xs" />
            Start {{ result.starting_position }}
          </q-chip>

          <!-- Faction -->
          <q-chip
            v-if="result.faction_name"
            dense
            color="indigo-2"
            text-color="indigo-9"
            size="sm"
          >
            <q-icon name="shield" size="14px" class="q-mr-xs" />
            {{ result.faction_name }}
          </q-chip>
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

// Store instance, reactive to league ID changes
const leagueStore = computed(() => useLeagueStore(user.value.myCurrentLeagueId)());

// First build a normalized list of results (from prop or store)
const rawResults = computed(() => {
  let src: any[] = [];

  if (props.matchResults) {
    // matchResults is keyed by player_profile, we need entries for this selected_game
    src = Object.values(props.matchResults)
      .flat()
      .filter((r: any) => r.selected_game === props.selectedGame.id);
  } else {
    src = leagueStore.value.matchResultsBySelectedGame[props.selectedGame.id] ?? [];
  }

  return src.map((r: any) => ({
    id: r.id,
    profile_name: r.player_profile_name,
    points: r.points ?? null,
    position: r.position ?? null,
    notes: r.notes ?? null,
    starting_position: r.starting_position ?? null,
    faction_name: r.faction_name ?? null,
  }));
});

// Final, sorted results:
// - If there are any points: sort by points desc
// - Otherwise: sort by position asc (nulls last)
const results = computed(() => {
  const mapped = rawResults.value.slice();

  const hasAnyPoints = mapped.some((r) => r.points != null);

  if (hasAnyPoints) {
    mapped.sort((a, b) => (b.points ?? 0) - (a.points ?? 0));
  } else {
    mapped.sort((a, b) => {
      if (a.position == null && b.position == null) return 0;
      if (a.position == null) return 1;
      if (b.position == null) return -1;
      return (a.position as number) - (b.position as number);
    });
  }

  return mapped;
});
</script>

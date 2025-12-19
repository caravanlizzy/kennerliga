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
        v-for="(result, index) in results"
        :key="result.id"
        class="match-result-item"
        :class="rowClass(index)"
      >
        <!-- Rank -->
        <q-item-section side class="q-pr-sm">
          <q-avatar
            size="34px"
            :color="rankColor(index)"
            :text-color="rankTextColor(index)"
            class="rank-avatar"
          >
            <span class="text-weight-bold">{{ index + 1 }}</span>
          </q-avatar>
        </q-item-section>

        <!-- Name + optional note -->
        <q-item-section>
          <q-item-label class="row items-center no-wrap">
            <q-icon
              v-if="index < 3"
              :name="rankIcon(index)"
              :color="rankColor(index)"
              size="18px"
              class="q-mr-xs"
            />
            <span class="text-weight-medium ellipsis">
              {{ result.profile_name }}
            </span>
          </q-item-label>

          <q-item-label v-if="result.notes" caption class="text-grey-7 ellipsis">
            <q-icon name="notes" size="14px" class="q-mr-xs" />
            {{ result.notes }}
          </q-item-label>
        </q-item-section>

        <!-- Stats -->
        <q-item-section side class="stats-col">
          <div class="row items-center justify-end q-gutter-xs">
            <q-badge
              v-if="result.points != null"
              :color="index === 0 ? 'amber-7' : 'grey-6'"
              class="stat-badge"
            >
              <q-icon name="star" size="14px" class="q-mr-xs" />
              {{ result.points }}
            </q-badge>

            <q-badge
              v-if="result.position != null"
              color="grey-5"
              class="stat-badge"
            >
              Pos {{ result.position }}
            </q-badge>

            <q-badge
              v-if="result.starting_position"
              color="grey-5"
              class="stat-badge"
            >
              <q-icon name="flag" size="14px" class="q-mr-xs" />
              {{ result.starting_position }}
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
    // The API now returns 'factions' as a list of objects with id, faction_name, level
    factions: (r.factions ?? [])
      .slice()
      .sort((a: any, b: any) => (a.level ?? 0) - (b.level ?? 0)),
  }));
});

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

function rankColor(index: number) {
  if (index === 0) return 'amber-7';
  if (index === 1) return 'blue-grey-5';
  if (index === 2) return 'brown-5';
  return 'grey-4';
}

function rankTextColor(index: number) {
  return index < 3 ? 'white' : 'grey-9';
}

function rankIcon(index: number) {
  if (index === 0) return 'emoji_events';
  if (index === 1) return 'workspace_premium';
  return 'military_tech';
}

function rowClass(index: number) {
  return {
    'is-first': index === 0,
    'is-podium': index < 3,
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

<template>
  <q-card flat bordered class="shadow-2 result-summary-card q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h6 text-primary">{{ gameName ?? '—' }}</div>
      <q-badge color="primary" label="Ergebnis" />
    </div>
    <q-separator class="q-mb-md" />

    <template v-if="results.length === 0">
      <div class="text-caption text-grey-7">Noch keine Ergebnisse.</div>
    </template>

    <q-list v-else>
      <q-item v-for="result in results" :key="result.id" class="q-py-sm">
        <q-item-section avatar class="q-pr-sm">
          <UserName :username="result.username" :color-class="result.colorClass" />
        </q-item-section>

        <q-item-section>
          <q-item-label class="text-weight-medium text-body1 q-mb-xs">
            {{ result.username }}
          </q-item-label>

          <q-item-label>
            <div class="row q-gutter-sm items-center no-wrap">
              <q-chip
                v-if="result.points != null"
                dense square color="grey-3" text-color="black"
                icon="star" :label="`${result.points} Punkte`"
              />
              <q-chip
                v-if="result.starting_position"
                dense square color="grey-2" text-color="black"
                icon="flag" :label="`Startpos. ${result.starting_position}`"
              />
              <q-chip
                v-if="result.faction_name"
                dense square color="indigo-1" text-color="indigo-10"
                icon="groups" :label="result.faction_name"
              />
            </div>
          </q-item-label>
        </q-item-section>
      </q-item>
    </q-list>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import UserName from 'components/ui/UserName.vue';
import { useLeagueStore } from 'stores/leagueStore';

const props = defineProps<{ selectedGameId: number }>();

const league = useLeagueStore();
const { matchResultsByGame, membersById, selectedGamesById } = storeToRefs(league);

// Game name via O(1) map
const gameName = computed(() => selectedGamesById.value[props.selectedGameId]?.game_name ?? null);

// Results for this game are already sorted in setResultsForGame()
const resultsForGame = computed(() => matchResultsByGame.value[props.selectedGameId] ?? []);

// Join once → template stays dumb & fast
const results = computed(() => {
  return resultsForGame.value.map(r => {
    const m = membersById.value[r.player_profile];
    return {
      id: r.id,
      username: m?.username ?? `#${r.player_profile}`,
      colorClass: m?.colorClass ?? 'bg-grey-2',
      points: r.points ?? null,
      starting_position: r.starting_position ?? null,
      faction_name: r.faction_name ?? null,
    };
  });
});
</script>

<style scoped>
.result-summary-card { border-radius: 10px; background: #fafafa; }
.q-chip { font-size: 0.75rem; }
</style>

<template>
  <q-card
    flat
    v-if="results.length > 0 || ptyResultMessage"
  >
    <div v-if="displayGameName" class="row items-center justify-center q-mb-xs">
      <div class="text-h6 text-weight-bold q-px-md q-py-sm">
        {{ selectedGame.game_name }}
      </div>
    </div>

    <template v-if="results.length === 0">
      <div class="text-center text-caption text-grey-7 q-py-md">
        No results uploaded.
      </div>
    </template>

    <template v-else>
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

          <!-- Player Name -->
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
          </q-item-section>

          <!-- Stats -->
          <q-item-section side class="row q-gutter-xs items-center">
            <!-- Points -->
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

            <!-- Starting Position -->
            <q-chip
              v-if="result.starting_position"
              dense
              color="grey-3"
              text-color="grey-8"
              size="sm"
            >
              <q-icon name="flag" size="14px" class="q-mr-xs" />
              {{ result.starting_position }}
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
    </template>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useLeagueStore } from 'stores/leagueStore';
import { QTableProps } from 'quasar';
import { useUserStore } from 'stores/userStore';

const props = withDefaults(
  defineProps<{
    selectedGame: any;
    displayGameName: boolean;
  }>(),
  {
    displayGameName: true,
  }
);
const { user } = storeToRefs(useUserStore());
const myLeagueStore = useLeagueStore(user.value.myCurrentLeagueId)();
const { matchResultsBySelectedGame, membersById } = storeToRefs(myLeagueStore);

// Results for this game are already sorted in setResultsForGame()
const resultsForGame = computed(
  () => matchResultsBySelectedGame.value[props.selectedGame.id] ?? []
);

// Join once → template stays dumb & fast
const results = computed(() => {
  return resultsForGame.value.map((r) => {
    const m = membersById.value[r.player_profile];
    return {
      id: r.id,
      profile_name: r.player_profile_name,
      points: r.points ?? null,
      starting_position: r.starting_position ?? null,
      faction_name: r.faction_name ?? null,
    };
  });
});
</script>

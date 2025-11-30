<template>
  <q-card flat>
    <div class="row items-center justify-around q-mb-md">
      <div class="text-h6 text-primary">{{ selectedGame.game_name }}</div>
      <!--      <q-badge color="primary" label="Ergebnis" />-->
    </div>

    <template v-if="results.length === 0">
      <div class="text-caption text-grey-7">No results uploaded.</div>
    </template>

    <template v-else>
      <q-table
        flat
        dense
        :rows="results"
        :columns="columns"
        row-key="id"
        hide-bottom
      >
        <!-- Player column -->
        <template v-slot:body-cell-player="props">
          <q-td :props="props">
            <q-chip :class="props.row.colorClass">
              {{ props.row.username }}
            </q-chip>
          </q-td>
        </template>
        <!-- Points -->
        <template v-slot:header-cell-points="props">
          <q-th :props="props" class="text-center">
            <q-icon name="star" size="sm" />
          </q-th>
        </template>
        <template v-slot:body-cell-points="props">
          <q-td :props="props">
            <q-chip
              v-if="props.row.points != null"
              dense
              square
              color="grey-3"
              text-color="black"
              :label="props.row.points"
            />
          </q-td>
        </template>

        <!-- Startpos -->
        <template v-slot:header-cell-starting_position="props">
          <q-th :props="props" class="text-center">
            <q-icon name="flag" size="sm" />
          </q-th>
        </template>
        <template v-slot:body-cell-starting_position="props">
          <q-td :props="props">
            <q-chip
              v-if="props.row.starting_position"
              dense
              square
              color="grey-2"
              text-color="black"
              :label="props.row.starting_position"
            />
          </q-td>
        </template>

        <!-- faction -->
        <template v-slot:header-cell-faction_name="props">
          <q-th :props="props" class="text-center">
            <q-icon name="diversity_2" size="sm" />
          </q-th>
        </template>
        <template v-slot:body-cell-faction_name="props">
          <q-td :props="props">
            <q-chip
              v-if="props.row.faction_name"
              dense
              square
              color="indigo-1"
              text-color="indigo-10"
              :label="props.row.faction_name"
            />
          </q-td>
        </template>
      </q-table>
    </template>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useLeagueStore } from 'stores/leagueStore';
import { QTableProps } from 'quasar';
import { useUserStore } from 'stores/userStore';

const props = defineProps<{ selectedGame: any }>();
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
      username: m?.username ?? `#${r.player_profile}`,
      points: r.points ?? null,
      starting_position: r.starting_position ?? null,
      faction_name: r.faction_name ?? null,
    };
  });
});

const columns: QTableProps['columns'] = [
  {
    name: 'player',
    label: '',
    field: 'username',
    align: 'left',
  },
  {
    name: 'points',
    label: '',
    field: 'points',
    align: 'center',
  },
  {
    name: 'starting_position',
    label: '',
    field: 'starting_position',
    align: 'center',
  },
  {
    name: 'faction_name',
    label: '',
    field: 'faction_name',
    align: 'center',
  },
];
</script>

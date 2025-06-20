<template>
  <div class="q-pa-md">
    <q-card flat bordered class="shadow-2 result-summary-card q-pa-md">
      <!-- Header -->
      <div class="row items-center justify-between q-mb-md">
        <div class="text-h6 text-primary">{{ gameName }}</div>
        <q-badge color="primary" label="Ergebnisse" />
      </div>

      <q-separator class="q-mb-md" />

      <!-- Results List -->
      <q-list>
        <q-item
          v-for="(result, index) in sortedResults"
          :key="result.id"
          class="q-py-sm"
        >
          <q-item-section avatar class="q-pr-sm">
            <UserName
              :username="result.username"
              :color-class="getPlayerColorClass(index)"
            />
          </q-item-section>

          <q-item-section>
            <q-item-label class="text-weight-medium text-body1 q-mb-xs">
              {{ result.username }}
            </q-item-label>

            <q-item-label>
              <div class="row q-gutter-sm items-center no-wrap">
                <q-chip
                  v-if="result.points !== undefined && result.points !== null"
                  dense
                  square
                  color="grey-3"
                  text-color="black"
                  icon="star"
                  :label="`${result.points} Punkte`"
                />
                <q-chip
                  v-if="result.starting_position"
                  dense
                  square
                  color="grey-2"
                  text-color="black"
                  icon="flag"
                  :label="`Startpos. ${result.starting_position}`"
                />
                <q-chip
                  v-if="result.faction_name"
                  dense
                  square
                  color="indigo-1"
                  text-color="indigo-10"
                  icon="groups"
                  :label="result.faction_name"
                />
              </div>
            </q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import UserName from 'components/ui/UserName.vue';

const props = defineProps<{
  gameName: string;
  results: Array<{
    id: number;
    username: string;
    points?: number;
    faction_name?: string;
    starting_position?: number;
  }>;
}>();

const sortedResults = computed(() => {
  return [...props.results].sort((a, b) => {
    if (a.points !== undefined && b.points !== undefined) {
      return b.points - a.points;
    }
    return 0;
  });
});

function getPlayerColorClass(index: number): string {
  return `bg-player-${(index % 6) + 1}`;
}
</script>

<style scoped>
.result-summary-card {
  border-radius: 10px;
  background: #fafafa;
}

.q-chip {
  font-size: 0.75rem;
}
</style>

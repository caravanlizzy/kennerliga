<template>
  <div>
    <div class="text-accent text-h6">Ergebniskonfiguration</div>
    <div class="q-gutter-md">
      <div class="row justify-between">
        <div class="text-bold">Spiel mit Punkten:</div>
        <YesNoItem :yes="hasPoints" />
      </div>

      <div class="row justify-between">
        <div class="text-bold">Startpunkte:</div>
        <div> {{ startingPointSystem.code }} <span
          class="text-italic">{{ startingPointSystem.description }} </span></div>
      </div>
      <div class="row justify-between">
        <div class="text-bold">StartspielerInreihenfolge</div>
        <YesNoItem :yes="hasStartingPlayerOrder" />
      </div>
      <div class="col">
        <div class="row justify-between">
          <div class="text-bold">Asymmetrisch</div>
          <YesNoItem :yes="isAsymmetric" />
        </div>
        <div class="row justify-between ">
          <div v-if="isAsymmetric" class="text-bold">
            Factions
          </div>
          <div v-if="isAsymmetric">
            <div v-for="faction of factions" :key="faction.id" class="inline-block faction">
              <div class="q-pa-xs ">{{ faction.name }}</div>
            </div>
          </div>
        </div>
      </div>
      <div class="row justify-between">
        <div> Tie Breaker</div>
        <div>
          <template v-if="tieBreakers.length > 0">
            <div v-for="(tieBreaker, index) in tieBreakers" :key="tieBreaker.order">
              {{ index + 1 }}. {{ tieBreaker.name }}
            </div>
          </template>
          <template v-else>
            Keine
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">

import OverviewCard from 'components/cards/OverviewCard.vue';
import YesNoItem from 'components/items/YesNoItem.vue';

defineProps<{
  hasPoints: boolean;
  startingPointSystem: { code: string, description: string };
  hasStartingPlayerOrder: boolean;
  isAsymmetric: boolean;
  factions: { id: number, name: string }[];
  tieBreakers: { id: number, name: string }[];
}>();
</script>

<style scoped>
.faction {
  //border: 1px solid grey;
}
</style>

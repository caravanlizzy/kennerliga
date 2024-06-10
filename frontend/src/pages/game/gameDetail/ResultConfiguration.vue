<template>
  <overview-card style="max-width: 500px">
    <template #cardHeader>
      Ergebniskonfiguration
    </template>
    <template #cardBody>
      <div class="q-gutter-md">
        <div class="row justify-between">
          <div>Spiel mit Punkten:</div>
          <YesNoItem :yes="hasPoints" />
        </div>

        <div class="row justify-between">
          <div>Startpunkte:</div>
          <div> {{startingPointSystem.code}} <span
            class="text-italic">{{ startingPointSystem.description }} </span></div>
        </div>
        <div class="row justify-between">
          <div>StartspielerInreihenfolge</div>
          <YesNoItem :yes="hasStartingPlayerOrder" />
        </div>
        <div class="col">
          <div class="row justify-between">
            <div>Asymmetrisch</div>
            <YesNoItem :yes="isAsymmetric" />
          </div>
          <div class="row justify-between ">
            <div flat v-if="isAsymmetric">
              Factions
            </div>
            <div v-if="isAsymmetric">
              <div v-for="faction of factions" :key="faction.id" class="inline-block faction q-ma-xs">
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
    </template>
  </overview-card>
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
  border: 1px solid black;
  border-radius: 3px;
}
</style>

<template>
  <div class="q-pa-sm">
    <div class="text-subtitle1 text-weight-medium text-dark q-mb-sm">Result configuration</div>

    <div class="column q-gutter-sm">

      <div class="row items-center justify-between">
        <div class="text-weight-medium">Points scoring</div>
        <YesNoItem :yes="hasPoints" />
      </div>

      <q-separator />

      <div class="row items-baseline justify-between">
        <div class="text-weight-medium q-mr-md">Starting point system</div>
        <div class="text-right">
          <div class="text-body2">{{ startingPointSystem.code }}</div>
          <div class="text-caption text-grey-7">{{ startingPointSystem.description }}</div>
        </div>
      </div>

      <q-separator />

      <div class="row items-center justify-between">
        <div class="text-weight-medium">Starting order</div>
        <YesNoItem :yes="hasStartingPlayerOrder" />
      </div>

      <q-separator />

      <div class="row items-center justify-between">
        <div class="text-weight-medium">Asymmetric</div>
        <YesNoItem :yes="isAsymmetric" />
      </div>

      <div v-if="isAsymmetric" class="q-pt-xs">
        <div class="text-caption text-grey-7 q-mb-xs">Factions</div>
        <div class="row q-col-gutter-xs">
          <div v-for="faction in factions" :key="faction.id" class="col-auto">
            <q-chip dense outline>{{ faction.name }}</q-chip>
          </div>
        </div>
      </div>

      <q-separator />

      <div class="row items-start justify-between">
        <div class="text-weight-medium q-mr-md">Tie-breakers</div>
        <div class="text-right">
          <template v-if="tieBreakers.length">
            <ol class="q-ma-none q-pa-none" style="list-style: decimal; padding-left: 1.25rem;">
              <li v-for="(tieBreaker) in tieBreakers" :key="tieBreaker.id" class="text-body2">
                {{ tieBreaker.name }}
              </li>
            </ol>
          </template>
          <template v-else>
            <span class="text-grey-7">None</span>
          </template>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import YesNoItem from 'components/base/YesNoItem.vue';

defineProps<{
  hasPoints: boolean;
  startingPointSystem: { code: string; description: string };
  hasStartingPlayerOrder: boolean;
  isAsymmetric: boolean;
  factions: { id: number; name: string }[];
  tieBreakers: { id: number; name: string }[];
}>();
</script>

<style scoped>
/* Keep styles minimal; layout handled via Quasar utility classes */
</style>

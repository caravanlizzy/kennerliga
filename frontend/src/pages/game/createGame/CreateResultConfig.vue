<template>
  <div class="q-mt-xl q-pa-md q-mx-md">
    <div class="text-h6 q-mb-md">Ergebnis konfigurieren</div>
    <div class="row">
      <q-card class="config-box q-pa-md">
        <div class="column ">
          <q-toggle label="Startspielerreihenfolge" :model-value="startingPlayerOrder"
                    @update:model-value="startingPlayerOrder = !startingPlayerOrder" />
          <q-separator />
          <q-toggle label="Punkte" :model-value="hasPoints" @update:model-value="hasPoints = !hasPoints" />
          <q-separator />
          <q-toggle label="Assymmentrisch" :model-value="isAssymmetric"
                    @update:model-value="isAssymmetric = !isAssymmetric" />
          <list-creator
            v-if="isAssymmetric"
            button-label="Neue Faction"
            @update-list="(updatedList: string[]) => factions = updatedList"
          ></list-creator>
          <q-separator />
          <q-toggle label="Tie Breaker" :model-value="hasTieBreaker"
                    @update:model-value="hasTieBreaker = !hasTieBreaker" />
          <list-creator
            button-label="Neuer Tiebreaker"
            v-if="hasTieBreaker"
            ranked
          />
        </div>
      </q-card>
    </div>
  </div>
</template>

<script setup lang="ts">

import { Ref, ref } from 'vue';
import ListCreator from 'components/lists/ListCreator.vue';

const isAssymmetric = ref(false);
const startingPlayerOrder = ref(true);
const hasPoints = ref(true);
const hasTieBreaker = ref(false);

const factions: Ref<string[]> = ref([]);

</script>


<style scoped>
.config-box {
  max-width: 300px;
}
</style>

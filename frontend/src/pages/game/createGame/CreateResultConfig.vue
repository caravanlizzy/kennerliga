<template>
  <div class="q-mt-xl q-pa-md">
    <div class="text-h6">Ergebnis konfigurieren</div>
    <div>
      <div class="flex">
        <div>
          <q-toggle label="Assymmentrisch" :model-value="isAssymmetric"
                    @update:model-value="isAssymmetric = !isAssymmetric"/>
          <list-creator v-if="isAssymmetric" button-label="Neue Faction" :initial-items="factions"
                        @update-list="(updatedList: string[]) => factions = updatedList"></list-creator>
        </div>
        <div>
          <q-toggle label="Startspielerreihenfolge" :model-value="startingPlayerOrder"
                    @update:model-value="startingPlayerOrder = !startingPlayerOrder"/>
        </div>
        <div>
          <q-toggle label="Punkte" :model-value="hasPoints" @update:model-value="hasPoints = !hasPoints"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">

import { ref } from 'vue';
import ListCreator from 'components/inputs/ListCreator.vue';

const isAssymmetric = ref(false);
const startingPlayerOrder = ref(true);
const hasPoints = ref(true);

const factions = ref([]);

</script>

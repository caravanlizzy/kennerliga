<template>
  <div class="q-mt-xl q-pa-md">
    <div class="text-h6 q-mb-md">Ergebnis konfigurieren</div>
    <div>
      <q-card class="config-box q-pa-md" >
        <div class="column ">
          <q-toggle label="Startspielerreihenfolge" :model-value="startingPlayerOrder"
                    @update:model-value="startingPlayerOrder = !startingPlayerOrder"/>
          <q-separator />
          <q-toggle label="Punkte" :model-value="hasPoints" @update:model-value="hasPoints = !hasPoints"/>
          <q-separator />
          <q-toggle label="Assymmentrisch" :model-value="isAssymmetric"
                    @update:model-value="isAssymmetric = !isAssymmetric"/>
          <div class="q-pa-md">
            <list-creator v-if="isAssymmetric" button-label="Neue Faction"
                          @update-list="(updatedList: string[]) => factions = updatedList"></list-creator>
          </div>
        </div>
      </q-card>
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


<style scoped>
.config-box {
  max-width: 300px;
}
</style>

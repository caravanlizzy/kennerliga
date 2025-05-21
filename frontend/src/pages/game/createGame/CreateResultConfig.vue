<template>
  <div class="q-mt-xl q-pa-md q-mx-md">
    <div class="text-h6 q-mb-md">Ergebnis konfigurieren</div>
    <div class="row">
      <q-card class="config-box q-pa-md">
        <div class="column ">
          <q-toggle label="Startspielerreihenfolge" :model-value="hasStartingPlayerOrder"
                    @update:model-value="hasStartingPlayerOrder = !hasStartingPlayerOrder" />
          <q-separator />
          <q-toggle label="Punkte" :model-value="hasPoints" @update:model-value="hasPoints = !hasPoints" />

          <kenner-select v-if="hasPoints" class="q-px-md q-pb-sm" v-model="startingPointSystem"
                         :options="startingPointSystemOptions" option-value="code" option-label="code"
                         label="Startsiegpunktesystem" />
          <div class="text-italic text-caption">{{startingPointSystem.description}}</div>
          <q-separator />
          <q-toggle label="Assymmentrisch" :model-value="isAsymmetric"
                    @update:model-value="isAsymmetric = !isAsymmetric" />
          <list-creator
            v-if="isAsymmetric"
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
            @update-list="(updatedList: string[]) => tieBreakers = updatedList"
          />
        </div>
      </q-card>
    </div>
  </div>
</template>

<script setup lang="ts">

import { Ref, ref, watch } from 'vue';
import ListCreator from 'components/lists/ListCreator.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import { api } from 'boot/axios';

import { TResultConfig } from 'src/types';

const emit = defineEmits<{
  (event: 'updateResultConfig', resultConfig: TResultConfig): void;
}>();

const isAsymmetric = ref(false);
const hasStartingPlayerOrder = ref(true);
const hasPoints = ref(true);
const hasTieBreaker = ref(false);
const tieBreakers: Ref<string[]> = ref([]);

const { data: startingPointSystemOptions } = await api('game/starting-point-systems');
const startingPointSystem = ref(startingPointSystemOptions[0]);
// const startingPointSystem = computed(() => startingPointSystemOptions.find(o => o.code === startingPointSystemCode.value));
const factions: Ref<string[]> = ref([]);


function getResultConfig(): TResultConfig {
  return ({
    isAsymmetric: isAsymmetric.value,
    hasPoints: hasPoints.value,
    startingPointSystem: startingPointSystem.value.id,
    hasStartingPlayerOrder: hasStartingPlayerOrder.value,
    factions: factions.value,
    hasTieBreaker: hasTieBreaker.value,
    tieBreakers: tieBreakers.value
  });
}

function emitResultConfig() {
  const resultConfig = getResultConfig();
  emit('updateResultConfig', resultConfig);
}

watch([isAsymmetric, hasPoints, startingPointSystem, hasStartingPlayerOrder, factions, hasTieBreaker, tieBreakers],
  () => emitResultConfig(), { immediate: true });

</script>


<style scoped>
.config-box {
  max-width: 300px;
}
</style>

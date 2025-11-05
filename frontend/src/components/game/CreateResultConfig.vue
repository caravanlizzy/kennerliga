<template>
  <div class="q-pa-md">
    <div class="text-subtitle1 text-weight-medium q-mb-md">
      Configure results
    </div>

    <q-card flat class="q-pa-sm rounded-borders">
      <div class="column">
        <!-- Starting Order -->
        <div class="row items-center justify-between q-pl-sm q-pr-sm">
          <div>
            <div class="text-body2">Starting order</div>
            <div class="text-caption text-grey-7">
              Who starts the first round?
            </div>
          </div>
          <q-toggle v-model="hasStartingPlayerOrder" dense />
        </div>

        <q-separator spaced />

        <!-- Points -->
        <div class="row items-center justify-between q-pl-sm q-pr-sm">
          <div>
            <div class="text-body2">Points scoring</div>
            <div class="text-caption text-grey-7">
              Enable victory points / scoring
            </div>
          </div>
          <q-toggle v-model="hasPoints" dense />
        </div>

        <!-- Point system -->
        <div class="q-pl-sm q-pr-sm q-mt-xs">
          <div v-if="loadingSystems" class="q-mt-sm">
            <q-skeleton type="QInput" />
          </div>
          <KennerSelect
            v-else
            class="full-width q-mt-sm"
            v-model="startingPointSystem"
            :options="startingPointSystemOptions"
            option-value="code"
            option-label="code"
            label="Starting point system"
            :disable="!hasPoints"
          />
          <div class="text-caption text-grey-7 q-mt-xs">
            {{ pointsDescription }}
          </div>
        </div>

        <q-separator spaced />

        <!-- Asymmetric -->
        <div class="row items-center justify-between q-pl-sm q-pr-sm">
          <div>
            <div class="text-body2">Asymmetric</div>
            <div class="text-caption text-grey-7">
              Different factions / starting conditions
            </div>
          </div>
          <q-toggle v-model="isAsymmetric" dense />
        </div>

        <div v-if="isAsymmetric" class="q-pl-sm q-pr-sm q-mt-sm">
          <list-creator
            button-label="New faction"
            @update-list="(updatedList: string[]) => (factions = updatedList)"
          />
          <div v-if="!factions.length" class="text-caption text-grey-7 q-mt-xs">
            No factions added yet.
          </div>
        </div>

        <q-separator spaced />

        <!-- Tie Breaker -->
        <div class="row items-center justify-between q-pl-sm q-pr-sm">
          <div>
            <div class="text-body2">Tie-breaker</div>
            <div class="text-caption text-grey-7">Rules for ties</div>
          </div>
          <q-toggle v-model="hasTieBreaker" dense />
        </div>

        <div v-if="hasTieBreaker" class="q-pl-sm q-pr-sm q-mt-sm">
          <list-creator
            button-label="New tie-breaker"
            ranked
            @update-list="(updatedList: string[]) => (tieBreakers = updatedList)"
          />
          <div
            v-if="!tieBreakers.length"
            class="text-caption text-grey-7 q-mt-xs"
          >
            No tie-breakers defined yet.
          </div>
        </div>
      </div>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import { Ref, ref, watch, computed } from 'vue';
import ListCreator from 'components/lists/ListCreator.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import { api } from 'boot/axios';
import { TResultConfig, TTieBreaker } from 'src/types';

const emit = defineEmits<{
  (event: 'updateResultConfig', resultConfig: TResultConfig): void;
}>();

const isAsymmetric = ref(false);
const hasStartingPlayerOrder = ref(true);
const hasPoints = ref(true);
const hasTieBreaker = ref(false);

const factions: Ref<string[]> = ref([]);
const tieBreakers: Ref<TTieBreaker[]> = ref([]);

const loadingSystems = ref(true);
const startingPointSystemOptions = ref<any[]>([]);
const startingPointSystem = ref<any | null>(null);

try {
  const { data } = await api('game/starting-point-systems');
  startingPointSystemOptions.value = data || [];
  startingPointSystem.value = startingPointSystemOptions.value[0] || null;
} finally {
  loadingSystems.value = false;
}

const pointsDescription = computed(() => {
  if (!hasPoints.value) return 'Points are disabled.';
  if (!startingPointSystem.value) return 'Select a point system.';
  return (
    startingPointSystem.value.description || 'Selected point system active.'
  );
});

const resultConfig = computed<TResultConfig>(() => ({
  isAsymmetric: isAsymmetric.value,
  hasPoints: hasPoints.value,
  startingPointSystem: startingPointSystem.value?.id ?? null,
  hasStartingPlayerOrder: hasStartingPlayerOrder.value,
  factions: factions.value,
  hasTieBreaker: hasTieBreaker.value,
  tieBreakers: tieBreakers.value,
}));

watch(resultConfig, (val) => emit('updateResultConfig', val), {
  immediate: true,
});
</script>

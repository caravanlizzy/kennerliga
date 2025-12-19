<template>
  <div class="q-pa-md">
    <div class="text-subtitle1 text-weight-medium q-mb-md">
      Configure results
    </div>

    <div class="q-mt-lg q-pa-md bg-grey-2 rounded-borders">
      <q-card flat bordered class="rounded-borders">
        <div class="column q-pa-sm">
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
            <div class="text-subtitle2 q-mb-xs">Primary Factions (Level 0)</div>
            <ListCreator
              button-label="Add level 0 faction"
              @update-list="(updatedList: string[]) => (factionsLevel0 = updatedList)"
            />

            <div class="q-mt-md">
              <div class="row items-center justify-between q-mb-xs">
                <div class="text-subtitle2">Secondary Factions (Level 1)</div>
                <q-toggle
                  v-model="hasSecondLevel"
                  dense
                  label="Enable Level 1"
                  left-label
                />
              </div>

              <div v-if="hasSecondLevel">
                <ListCreator
                  button-label="Add level 1 faction"
                  @update-list="(updatedList: string[]) => (factionsLevel1 = updatedList)"
                />
              </div>
            </div>

            <div
              v-if="!factionsLevel0.length && !factionsLevel1.length"
              class="text-caption text-grey-7 q-mt-xs"
            >
              No factions added yet.
            </div>
          </div>

          <q-separator spaced />

          <!-- Tie Breakers -->
          <div class="row items-center justify-between q-pl-sm q-pr-sm">
            <div>
              <div class="text-body2">Tie-breakers</div>
              <div class="text-caption text-grey-7">
                Rules for ties (top to bottom priority)
              </div>
            </div>
            <q-toggle v-model="hasTieBreaker" dense />
          </div>

          <div v-if="hasTieBreaker" class="q-pl-sm q-pr-sm q-mt-sm">
            <div class="row items-center justify-between q-mb-xs">
              <div class="text-subtitle2">Tie-breakers</div>
              <q-btn
                flat
                dense
                icon="add"
                label="New tie-breaker"
                color="primary"
                @click="addTieBreaker"
              />
            </div>

            <div
              v-if="!tieBreakersUi.length"
              class="text-caption text-grey-7 q-mt-xs"
            >
              No tie-breakers defined yet.
            </div>

            <div v-else class="q-mt-sm">
              <div
                v-for="tb in tieBreakersUi"
                :key="tb.id"
                class="q-mb-sm q-pa-sm bg-white rounded-borders"
              >
                <div class="row items-center q-col-gutter-sm">
                  <div class="col">
                    <KennerInput
                      dense
                      v-model="tb.name"
                      label="Tie-breaker name"
                    />
                  </div>

                  <div class="col-auto">
                    <q-checkbox
                      dense
                      v-model="tb.lowerWins"
                      label="Lower wins"
                    />
                  </div>

                  <div class="col-auto">
                    <q-btn
                      flat
                      dense
                      icon="delete"
                      color="negative"
                      @click="removeTieBreaker(tb.id)"
                    />
                  </div>
                </div>

                <div class="text-caption text-grey-7 q-mt-xs">
                  {{
                    tb.lowerWins ? 'Lower numbers win' : 'Higher numbers win'
                  }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </q-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import KennerInput from 'components/base/KennerInput.vue';
import ListCreator from 'components/lists/ListCreator.vue';
import { api } from 'boot/axios';
import { TFaction, TResultConfig, TTieBreaker } from 'src/types';

const emit = defineEmits<{
  (event: 'updateResultConfig', resultConfig: TResultConfig): void;
}>();

type UiTieBreaker = {
  id: string;
  name: string;
  lowerWins: boolean; // checked => lower wins
};

function newRef(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    // @ts-expect-error TS lib may not include randomUUID depending on config
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

const isAsymmetric = ref(false);
const hasStartingPlayerOrder = ref(true);
const hasPoints = ref(true);
const hasTieBreaker = ref(false);
const hasSecondLevel = ref(false);

const factionsLevel0 = ref<string[]>([]);
const factionsLevel1 = ref<string[]>([]);
const tieBreakersUi = ref<UiTieBreaker[]>([]);

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

function addTieBreaker(): void {
  tieBreakersUi.value.unshift({
    id: newRef(),
    name: '',
    lowerWins: false, // default: higher wins
  });
}

function removeTieBreaker(id: string): void {
  tieBreakersUi.value = tieBreakersUi.value.filter((t) => t.id !== id);
}

const tieBreakers = computed<TTieBreaker[]>(() => {
  return tieBreakersUi.value.map((tb) => ({
    name: tb.name,
    higher_wins: !tb.lowerWins,
  }));
});

const factions = computed<TFaction[]>(() => {
  if (!isAsymmetric.value) return [];
  const level0: TFaction[] = factionsLevel0.value.map((name) => ({
    name,
    level: 0,
  }));

  const level1: TFaction[] = hasSecondLevel.value
    ? factionsLevel1.value.map((name) => ({ name, level: 1 }))
    : [];

  return [...level0, ...level1];
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

watch(
  resultConfig,
  (val) => {
    emit('updateResultConfig', val);
  },
  {
    immediate: true,
    deep: true,
  }
);
</script>

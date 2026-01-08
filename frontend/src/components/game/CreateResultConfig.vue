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
            <div v-for="(levelData, index) in factionLevels" :key="levelData.id" class="q-mb-md">
              <div class="row items-center justify-between q-mb-xs">
                <div class="text-subtitle2">
                  {{ index === 0 ? 'Primary' : 'Secondary' }} Factions (Level {{ index }})
                </div>
                <KennerButton
                  v-if="index > 0"
                  flat
                  dense
                  round
                  icon="delete"
                  color="negative"
                  size="sm"
                  @click="removeFactionLevel(index)"
                >
                  <q-tooltip>Remove level {{ index }}</q-tooltip>
                </KennerButton>
              </div>
              <ListCreator
                :button-label="`Add level ${index} faction`"
                :initial-list="levelData.factions"
                @update-list="(updatedList: string[]) => (levelData.factions = updatedList)"
              />
            </div>

            <div class="row justify-center q-mt-sm">
              <KennerButton
                flat
                dense
                icon="add"
                label="Add faction level"
                color="primary"
                @click="addFactionLevel"
              />
            </div>

            <div
              v-if="!factionLevels.some(l => l.factions.length)"
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
              <KennerButton
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
                v-for="(tb, tbIdx) in tieBreakersUi"
                :key="tb.id"
                class="q-mb-sm q-pa-sm bg-white rounded-borders shadow-1 border-light"
              >
                <div class="row items-center q-col-gutter-sm">
                  <div class="col-auto">
                    <div class="column">
                      <KennerButton
                        flat
                        round
                        dense
                        size="xs"
                        icon="keyboard_arrow_up"
                        :disable="tbIdx === 0"
                        @click="moveTieBreaker(tbIdx, 'up')"
                      />
                      <KennerButton
                        flat
                        round
                        dense
                        size="xs"
                        icon="keyboard_arrow_down"
                        :disable="tbIdx === tieBreakersUi.length - 1"
                        @click="moveTieBreaker(tbIdx, 'down')"
                      />
                    </div>
                  </div>
                  <div class="col">
                    <KennerInput
                      v-model="tb.name"
                      label="Tie-breaker name"
                      placeholder="e.g. Most coins, Strength..."
                    />
                  </div>

                  <div class="col-auto">
                    <q-checkbox
                      dense
                      v-model="tb.lowerWins"
                      label="Lower wins"
                      color="primary"
                    />
                  </div>

                  <div class="col-auto">
                    <KennerButton
                      flat
                      round
                      dense
                      icon="delete"
                      color="negative"
                      @click="removeTieBreaker(tb.id)"
                    />
                  </div>
                </div>

                <div class="text-caption text-grey-7 q-mt-xs q-ml-xl">
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
import KennerButton from 'components/base/KennerButton.vue';
import ListCreator from 'components/lists/ListCreator.vue';
import { api } from 'boot/axios';
import { TFaction, TResultConfig, TTieBreaker } from 'src/types';

const props = defineProps<{
  initialConfig?: TResultConfig;
}>();

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

const isAsymmetric = ref(props.initialConfig?.isAsymmetric ?? false);
const hasStartingPlayerOrder = ref(
  props.initialConfig?.hasStartingPlayerOrder ?? true
);
const hasPoints = ref(props.initialConfig?.hasPoints ?? true);
const hasTieBreaker = ref(props.initialConfig?.hasTieBreaker ?? false);

type UiFactionLevel = {
  id: string;
  factions: string[];
};

const factionLevels = ref<UiFactionLevel[]>([]);

// Initialize from props
if (props.initialConfig?.factions && props.initialConfig.factions.length > 0) {
  const maxLevel = Math.max(
    ...props.initialConfig.factions.map((f) => f.level),
    0
  );
  for (let i = 0; i <= maxLevel; i++) {
    factionLevels.value.push({
      id: newRef(),
      factions: props.initialConfig.factions
        .filter((f) => f.level === i)
        .map((f) => f.name),
    });
  }
} else {
  factionLevels.value = [{ id: newRef(), factions: [] }]; // Start with level 0
}

const tieBreakersUi = ref<UiTieBreaker[]>(
  props.initialConfig?.tieBreakers?.map((tb) => ({
    id: newRef(),
    name: tb.name,
    lowerWins: !tb.higher_wins,
  })) ?? []
);

const loadingSystems = ref(true);
const startingPointSystemOptions = ref<any[]>([]);
const startingPointSystem = ref<any | null>(null);

try {
  const { data } = await api('game/starting-point-systems');
  startingPointSystemOptions.value = data || [];

  if (props.initialConfig?.startingPointSystem) {
    startingPointSystem.value =
      startingPointSystemOptions.value.find(
        (s) => s.id === props.initialConfig?.startingPointSystem
      ) ||
      startingPointSystemOptions.value[0] ||
      null;
  } else {
    startingPointSystem.value = startingPointSystemOptions.value[0] || null;
  }
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
  tieBreakersUi.value.push({
    id: newRef(),
    name: '',
    lowerWins: false, // default: higher wins
  });
}

function moveTieBreaker(index: number, direction: 'up' | 'down') {
  const newIndex = direction === 'up' ? index - 1 : index + 1;
  if (newIndex < 0 || newIndex >= tieBreakersUi.value.length) return;
  const temp = tieBreakersUi.value[index];
  tieBreakersUi.value[index] = tieBreakersUi.value[newIndex];
  tieBreakersUi.value[newIndex] = temp;
}

function removeTieBreaker(id: string): void {
  tieBreakersUi.value = tieBreakersUi.value.filter((t) => t.id !== id);
}

function addFactionLevel(): void {
  factionLevels.value.push({ id: newRef(), factions: [] });
}

function removeFactionLevel(index: number): void {
  if (index > 0) {
    factionLevels.value.splice(index, 1);
  }
}

const tieBreakers = computed<TTieBreaker[]>(() => {
  return tieBreakersUi.value.map((tb) => ({
    name: tb.name,
    higher_wins: !tb.lowerWins,
  }));
});

const factions = computed<TFaction[]>(() => {
  if (!isAsymmetric.value) return [];
  const allFactions: TFaction[] = [];

  factionLevels.value.forEach((levelData, level) => {
    levelData.factions.forEach((name) => {
      allFactions.push({ name, level });
    });
  });

  return allFactions;
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

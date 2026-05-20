<template>
  <div class="q-pa-lg">
    <div class="text-h5 text-weight-bold text-dark q-mb-lg row items-center">
      <q-icon name="analytics" color="primary" class="q-mr-sm" />
      Result Configuration
    </div>

    <div class="column q-gutter-y-md">
      <div class="row items-center justify-between bg-grey-1 q-pa-md rounded-borders shadow-1">
        <div>
          <div class="text-subtitle1 text-weight-bold">Points Scoring</div>
          <div class="text-caption text-grey-7">Is victory point tracking enabled?</div>
        </div>
        <YesNoItem :yes="hasPoints" />
      </div>

      <div class="row items-center justify-between bg-grey-1 q-pa-md rounded-borders shadow-1">
        <div>
          <div class="text-subtitle1 text-weight-bold">Starting Point System</div>
          <div class="text-caption text-grey-7">{{ startingPointSystemDescription }}</div>
        </div>
        <div class="text-right">
          <q-badge color="primary" label-class="text-weight-bold" class="q-px-sm q-py-xs">
            {{ startingPointSystemCode }}
          </q-badge>
        </div>
      </div>

      <div class="row items-center justify-between bg-grey-1 q-pa-md rounded-borders shadow-1">
        <div>
          <div class="text-subtitle1 text-weight-bold">Starting Order</div>
          <div class="text-caption text-grey-7">Does the game track player turn order?</div>
        </div>
        <YesNoItem :yes="hasStartingPlayerOrder" />
      </div>

      <div class="row items-center justify-between bg-grey-1 q-pa-md rounded-borders shadow-1">
        <div>
          <div class="text-subtitle1 text-weight-bold">Asymmetric Play</div>
          <div class="text-caption text-grey-7">Are there unique factions or powers?</div>
        </div>
        <YesNoItem :yes="isAsymmetric" />
      </div>

      <div v-if="isAsymmetric" class="q-pa-md bg-white border-light rounded-borders">
        <div class="text-subtitle2 text-grey-8 q-mb-sm border-bottom q-pb-xs">Factions</div>
        <div class="row q-col-gutter-sm">
          <div v-for="faction in sortedFactions" :key="faction.id" class="col-auto">
            <q-chip dense outline color="primary" icon="groups">{{ faction.name }}</q-chip>
          </div>
        </div>
      </div>

      <div class="q-pa-md bg-grey-1 rounded-borders shadow-1">
        <div class="row items-center justify-between q-mb-sm">
          <div class="text-subtitle1 text-weight-bold">Win Conditions</div>
          <q-icon name="emoji_events" color="grey-6" />
        </div>
        <div v-if="sortedWinConditions.length">
          <div
            v-for="(wc, wcIndex) in sortedWinConditions"
            :key="wc.id"
            class="q-mb-md q-pa-sm bg-white rounded-borders shadow-1"
          >
            <div class="row items-center q-mb-xs">
              <q-avatar size="24px" color="primary" text-color="white" class="q-mr-sm text-caption">
                {{ wcIndex + 1 }}
              </q-avatar>
              <div class="text-body2 text-weight-bold">{{ wc.name }}</div>
              <q-chip
                dense
                outline
                size="sm"
                class="q-ml-sm"
                :color="wc.condition_type === 'POINTS' ? 'primary' : 'secondary'"
              >
                {{ wc.condition_type === 'POINTS' ? 'Points' : 'Option' }}
              </q-chip>
            </div>

            <div v-if="wc.condition_type === 'OPTION' && wc.options?.length" class="q-mt-sm q-pl-md">
              <div class="text-caption text-grey-7 q-mb-xs">Options</div>
              <div class="row q-col-gutter-xs">
                <div v-for="opt in [...wc.options].sort((a, b) => (a.order ?? 0) - (b.order ?? 0))" :key="opt.id" class="col-auto">
                  <q-chip dense outline color="secondary" size="sm">{{ opt.name }}</q-chip>
                </div>
              </div>
            </div>

            <div v-if="wc.tie_breakers?.length" class="q-mt-sm q-pl-md">
              <div class="text-caption text-grey-7 q-mb-xs">Tie-breakers</div>
              <div
                v-for="(tb, tbIndex) in [...wc.tie_breakers].sort((a, b) => (b.order ?? 0) - (a.order ?? 0))"
                :key="tb.id"
                class="row items-center q-mb-xs"
              >
                <q-avatar size="18px" color="secondary" text-color="white" class="q-mr-sm text-caption">
                  {{ tbIndex + 1 }}
                </q-avatar>
                <div class="text-caption">
                  {{ tb.name }}
                  <span class="text-grey-6">({{ tb.higher_wins ? 'higher wins' : 'lower wins' }})</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-caption text-grey-6 italic">
          No win conditions defined.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import YesNoItem from 'components/base/YesNoItem.vue';
import { computed } from 'vue';

type WinConditionView = {
  id: number;
  name: string;
  condition_type: 'POINTS' | 'OPTION';
  order?: number;
  options?: { id: number; name: string; order?: number }[];
  tie_breakers?: { id: number; name: string; order?: number; higher_wins: boolean }[];
};

const props = defineProps<{
  hasPoints: boolean;
  startingPointSystemCode: string;
  startingPointSystemDescription: string;
  hasStartingPlayerOrder: boolean;
  isAsymmetric: boolean;
  factions: { id: number; name: string; level?: number }[];
  winConditions: WinConditionView[];
}>();

const sortedWinConditions = computed(() =>
  [...props.winConditions].sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
);

const sortedFactions = computed(() => {
  return [...props.factions].sort((a, b) => (a.level ?? 0) - (b.level ?? 0));
});
</script>

<template>
  <div class="column q-gutter-y-md">
    <!-- Config Grid -->
    <div class="row q-col-gutter-sm">
      <div class="col-12 col-sm-6">
        <div class="config-stat-card q-pa-md row items-center justify-between">
          <div class="column">
            <span class="text-subtitle2 text-weight-bold text-dark">Points Scoring</span>
            <span class="text-caption text-grey-6">Victory point tracking</span>
          </div>
          <q-badge :color="hasPoints ? 'positive' : 'grey-5'" class="q-px-sm" rounded>
            <YesNoItem :yes="hasPoints" />
          </q-badge>
        </div>
      </div>

      <div class="col-12 col-sm-6">
        <div class="config-stat-card q-pa-md row items-center justify-between">
          <div class="column">
            <span class="text-subtitle2 text-weight-bold text-dark">Starting Point System</span>
            <span class="text-caption text-grey-6">{{ startingPointSystemDescription }}</span>
          </div>
          <q-badge color="primary" class="q-px-sm" rounded>
            {{ startingPointSystemCode }}
          </q-badge>
        </div>
      </div>

      <div class="col-12 col-sm-6">
        <div class="config-stat-card q-pa-md row items-center justify-between">
          <div class="column">
            <span class="text-subtitle2 text-weight-bold text-dark">Starting Order</span>
            <span class="text-caption text-grey-6">Turn order tracking</span>
          </div>
          <q-badge :color="hasStartingPlayerOrder ? 'positive' : 'grey-5'" class="q-px-sm" rounded>
            <YesNoItem :yes="hasStartingPlayerOrder" />
          </q-badge>
        </div>
      </div>

      <div class="col-12 col-sm-6">
        <div class="config-stat-card q-pa-md row items-center justify-between">
          <div class="column">
            <span class="text-subtitle2 text-weight-bold text-dark">Asymmetric Play</span>
            <span class="text-caption text-grey-6">Unique factions & powers</span>
          </div>
          <q-badge :color="isAsymmetric ? 'secondary' : 'grey-5'" class="q-px-sm" rounded>
            <YesNoItem :yes="isAsymmetric" />
          </q-badge>
        </div>
      </div>
    </div>

    <!-- Factions Section -->
    <div v-if="isAsymmetric && sortedFactions.length" class="config-section-card q-pa-md">
      <div class="text-caption text-weight-bold text-grey-7 q-mb-sm text-uppercase tracking-wide">
        Factions & Roles
      </div>
      <div class="row q-gutter-xs">
        <q-chip
          v-for="faction in sortedFactions"
          :key="faction.id"
          dense
          color="primary"
          outline
          icon="groups"
          class="text-weight-medium"
        >
          {{ faction.name }}
        </q-chip>
      </div>
    </div>

    <!-- Win Conditions -->
    <div class="config-section-card q-pa-md">
      <div class="row items-center justify-between q-mb-sm">
        <div class="text-caption text-weight-bold text-grey-7 text-uppercase tracking-wide row items-center q-gutter-x-xs">
          <span>Win Conditions</span>
          <q-icon name="emoji_events" color="warning" size="16px" />
        </div>
        <q-badge v-if="sortedWinConditions.length" color="primary" rounded class="q-px-xs">
          {{ sortedWinConditions.length }}
        </q-badge>
      </div>

      <div v-if="sortedWinConditions.length" class="column q-gutter-y-sm">
        <div
          v-for="(wc, wcIndex) in sortedWinConditions"
          :key="wc.id"
          class="win-condition-item q-pa-sm rounded-borders bg-grey-1"
        >
          <div class="row items-center justify-between no-wrap">
            <div class="row items-center q-gutter-x-sm no-wrap">
              <q-avatar size="22px" color="primary" text-color="white" class="text-caption text-weight-bolder">
                {{ wcIndex + 1 }}
              </q-avatar>
              <span class="text-body2 text-weight-bold text-dark">{{ wc.name }}</span>
            </div>
            <q-badge
              outline
              :color="wc.condition_type === 'POINTS' ? 'primary' : 'secondary'"
              class="text-weight-bold"
            >
              {{ wc.condition_type === 'POINTS' ? 'Points' : 'Option' }}
            </q-badge>
          </div>

          <!-- Options -->
          <div v-if="wc.condition_type === 'OPTION' && wc.options?.length" class="row q-gutter-xs q-mt-xs q-ml-md">
            <q-chip
              v-for="opt in [...wc.options].sort((a, b) => (a.order ?? 0) - (b.order ?? 0))"
              :key="opt.id"
              dense
              size="sm"
              color="secondary"
              outline
              icon="radio_button_checked"
            >
              {{ opt.name }}
            </q-chip>
          </div>

          <!-- Tie-breakers -->
          <div v-if="wc.tie_breakers?.length" class="q-mt-xs q-ml-md">
            <div
              v-for="tb in [...wc.tie_breakers].sort((a, b) => (b.order ?? 0) - (a.order ?? 0))"
              :key="tb.id"
              class="row items-center text-caption text-grey-8 q-gutter-x-xs q-my-xs"
            >
              <q-icon name="subdirectory_arrow_right" color="grey-6" size="14px" />
              <span class="text-weight-medium">{{ tb.name }}</span>
              <span class="text-grey-6 text-caption">({{ tb.higher_wins ? 'higher wins' : 'lower wins' }})</span>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="text-caption text-grey-6 italic text-center q-py-sm">
        No win conditions defined.
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

<style scoped lang="scss">
.config-stat-card {
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
}

.config-section-card {
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
}

.win-condition-item {
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.tracking-wide {
  letter-spacing: 0.5px;
}
</style>

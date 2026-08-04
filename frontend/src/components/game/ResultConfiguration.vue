<template>
  <div>
    <q-list separator padding>
      <q-item>
        <q-item-section>
          <q-item-label class="text-weight-bold text-subtitle1">Points Scoring</q-item-label>
          <q-item-label caption>Is victory point tracking enabled?</q-item-label>
        </q-item-section>
        <q-item-section side>
          <q-badge :color="hasPoints ? 'positive' : 'grey-7'" class="q-px-sm">
            <YesNoItem :yes="hasPoints" />
          </q-badge>
        </q-item-section>
      </q-item>

      <q-item>
        <q-item-section>
          <q-item-label class="text-weight-bold text-subtitle1">Starting Point System</q-item-label>
          <q-item-label caption>{{ startingPointSystemDescription }}</q-item-label>
        </q-item-section>
        <q-item-section side>
          <q-badge color="primary" class="q-px-sm">
            {{ startingPointSystemCode }}
          </q-badge>
        </q-item-section>
      </q-item>

      <q-item>
        <q-item-section>
          <q-item-label class="text-weight-bold text-subtitle1">Starting Order</q-item-label>
          <q-item-label caption>Does the game track player turn order?</q-item-label>
        </q-item-section>
        <q-item-section side>
          <q-badge :color="hasStartingPlayerOrder ? 'positive' : 'grey-7'" class="q-px-sm">
            <YesNoItem :yes="hasStartingPlayerOrder" />
          </q-badge>
        </q-item-section>
      </q-item>

      <q-item>
        <q-item-section>
          <q-item-label class="text-weight-bold text-subtitle1">Asymmetric Play</q-item-label>
          <q-item-label caption>Are there unique factions or powers?</q-item-label>
        </q-item-section>
        <q-item-section side>
          <q-badge :color="isAsymmetric ? 'secondary' : 'grey-7'" class="q-px-sm">
            <YesNoItem :yes="isAsymmetric" />
          </q-badge>
        </q-item-section>
      </q-item>

      <div v-if="isAsymmetric" class="q-mx-md q-my-sm q-pa-md bg-grey-1 rounded-borders border-light">
        <div class="text-caption text-weight-bold text-grey-9 q-mb-sm uppercase-label" style="font-size: 0.65rem">Factions</div>
        <div class="row q-col-gutter-md">
          <div v-for="faction in sortedFactions" :key="faction.id" class="col-auto">
            <div class="row items-center q-gutter-x-xs">
              <q-icon name="groups" color="primary" size="xs" />
              <div class="text-body2 text-grey-9 text-weight-medium">{{ faction.name }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="q-mt-lg">
        <div class="q-px-md q-pb-md text-weight-bold text-subtitle1 row items-center uppercase-label text-grey-9">
          Win Conditions
          <q-icon name="emoji_events" color="warning" class="q-ml-sm" />
        </div>

        <div v-if="sortedWinConditions.length">
          <q-list separator class="bg-white">
            <q-item
              v-for="(wc, wcIndex) in sortedWinConditions"
              :key="wc.id"
              class="q-py-md"
            >
              <q-item-section avatar>
                <q-avatar size="24px" color="primary" text-color="white">
                  {{ wcIndex + 1 }}
                </q-avatar>
              </q-item-section>
              <q-item-section>
                <q-item-label class="text-weight-bold text-body1 text-grey-9">{{ wc.name }}</q-item-label>
                <q-item-label v-if="wc.condition_type === 'OPTION' && wc.options?.length" caption>
                  <div class="row q-col-gutter-md q-mt-xs">
                    <div v-for="opt in [...wc.options].sort((a, b) => (a.order ?? 0) - (b.order ?? 0))" :key="opt.id" class="col-auto">
                      <div class="row items-center q-gutter-x-xs">
                        <q-icon name="radio_button_checked" color="secondary" size="xs" />
                        <div class="text-body2 text-grey-9">{{ opt.name }}</div>
                      </div>
                    </div>
                  </div>
                </q-item-label>

                <div v-if="wc.tie_breakers?.length" class="q-mt-sm">
                  <div class="text-caption text-weight-bold text-grey-9 q-mb-xs uppercase-label" style="font-size: 0.65rem">Tie-breakers</div>
                  <div
                    v-for="tb in [...wc.tie_breakers].sort((a, b) => (b.order ?? 0) - (a.order ?? 0))"
                    :key="tb.id"
                    class="row items-center q-mb-xs"
                  >
                    <q-icon name="subdirectory_arrow_right" color="grey-6" size="xs" class="q-mr-xs" />
                    <div class="text-caption">
                      <span class="text-weight-medium text-grey-9">{{ tb.name }}</span>
                      <span class="text-grey-6 q-ml-xs">({{ tb.higher_wins ? 'higher wins' : 'lower wins' }})</span>
                    </div>
                  </div>
                </div>
              </q-item-section>
              <q-item-section side>
                <q-badge
                  outline
                  :color="wc.condition_type === 'POINTS' ? 'primary' : 'secondary'"
                >
                  {{ wc.condition_type === 'POINTS' ? 'Points' : 'Option' }}
                </q-badge>
              </q-item-section>
            </q-item>
          </q-list>
        </div>
        <div v-else class="q-px-md q-pb-md text-caption text-grey-6 italic">
          No win conditions defined.
        </div>
      </div>
    </q-list>
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

<style scoped>
.border-light {
  border: 1px solid #e0e0e0;
}
.uppercase-label {
  text-transform: uppercase;
  letter-spacing: 1px;
}
</style>

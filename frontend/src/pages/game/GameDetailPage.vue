
<template>
  <div class="q-pa-md">
    <!-- Loading State -->
    <div v-if="isLoading" class="flex flex-center q-pa-xl">
      <q-spinner-puff color="accent" size="3em" />
    </div>

    <div v-else>
      <!-- Header Section -->
      <div class="q-mb-lg">
        <p class="text-h5 q-mb-xs">{{ game.name }}</p>
        <q-badge color="primary" outline class="q-pa-sm">
          {{ platform.name }}
        </q-badge>
      </div>

      <!-- Options Section -->
      <div class="q-mb-lg q-pa-md bg-grey-2 rounded-borders">
        <span class="text-h6 q-mb-md block">Game Options</span>

        <div v-if="!hasOptions" class="text-caption text-grey-7 q-pa-sm">
          No options configured for this game.
        </div>

        <div v-else class="row q-col-gutter-md">
          <!-- Enabled/Disabled Options Card -->
          <div
            v-if="yesNoOptions.length"
            class="col-12 col-sm-6 col-md-4"
          >
            <q-card flat bordered class="full-height">
              <q-card-section>
                <div class="text-subtitle1 text-weight-medium text-secondary q-mb-sm">
                  Enabled/Disabled Options
                </div>
                <q-list dense>
                  <q-item v-for="option in yesNoOptions" :key="option.id" class="q-px-none">
                    <q-item-section avatar class="items-center" style="min-width: 24px;">
                      <q-icon name="check_circle" color="positive" size="xs" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>{{ option.name }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>
          </div>

          <!-- Choice Options Cards -->
          <div
            v-for="option in choiceOptions"
            :key="option.id"
            class="col-12 col-sm-6 col-md-4"
          >
            <q-card flat bordered class="full-height">
              <q-card-section>
                <div class="text-subtitle1 text-weight-medium text-secondary q-mb-sm">
                  {{ option.name }}
                </div>
                <q-list dense>
                  <q-item
                    v-for="choice in option.choices"
                    :key="choice.name"
                    class="q-px-none"
                  >
                    <q-item-section avatar class="items-center" style="min-width: 24px;">
                      <q-icon name="circle" color="grey-5" size="6px" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>{{ choice.name }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </div>

      <!-- Result Configuration Section -->
      <div class="q-pa-md bg-grey-2 rounded-borders">
        <span class="text-h6 q-mb-md block">Result Configuration</span>

        <div class="row q-col-gutter-md">
          <div class="col-12">
            <q-card flat bordered>
              <q-card-section>
                <ResultConfiguration
                  :isHighlighed="true"
                  :hasPoints="resultConfig.has_points"
                  :startingPointSystem="startingPointSystem"
                  :hasStartingPlayerOrder="resultConfig.has_starting_player_order"
                  :isAsymmetric="resultConfig.is_asymmetric"
                  :factions="factions"
                  :tieBreakers="tieBreakers"
                />
              </q-card-section>
            </q-card>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { api } from 'boot/axios';
import { useRoute } from 'vue-router';
import ResultConfiguration from 'components/game/ResultConfiguration.vue';
import { computed, ref } from 'vue';

const route = useRoute();
const isLoading = ref(true);

const { data: game } = await api(`game/games-full/${route.params.id}`);
const { data: [resultConfig] } = await api(`game/result-configs/?game=${route.params.id}`);
const { data: tieBreakers } = await api(`game/tie-breakers/?result_config=${resultConfig.id}`);
const { data: factions } = await api(`game/factions/?game=${route.params.id}`);
const { data: platform } = await api(`game/platforms/${game.platform}`);
const { data: startingPointSystem } = await api(
  `game/starting-point-systems/${resultConfig.starting_points_system}`
);

isLoading.value = false;

// Filter yesNoOptions (those without choices)
const yesNoOptions = computed(() =>
  game.options.filter((option: any) => !option.has_choices)
);

// Filter the choiceOptions (those with existing choices)
const choiceOptions = computed(() =>
  game.options.filter((option: any) => option.has_choices)
);

// Check if there are any options
const hasOptions = computed(() =>
  yesNoOptions.value.length > 0 || choiceOptions.value.length > 0
);
</script>

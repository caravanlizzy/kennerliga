<template>
  <q-page padding>
    <div v-if="isLoading" class="flex flex-center q-pa-xl">
      <q-spinner-puff color="primary" size="3em" />
    </div>

    <div v-else class="row justify-center">
      <div class="col-12 col-md-10 col-lg-8">
        <!-- Header -->
        <q-card flat bordered class="q-mb-lg shadow-2 overflow-hidden">
          <q-card-section class="bg-primary text-white q-pa-lg">
            <div class="row items-center justify-between">
              <div>
                <div class="text-h3 text-weight-bold">{{ game.name }}</div>
                <div class="text-subtitle1 opacity-80">{{ platform.name }}</div>
              </div>
              <div class="row q-gutter-sm">
                <KennerButton
                  unelevated
                  color="white"
                  text-color="primary"
                  icon="edit"
                  label="Edit Game"
                  @click="router.push({ name: 'game-edit', params: { id: game.id } })"
                />
              </div>
            </div>
          </q-card-section>

          <q-card-section class="q-pa-md bg-grey-1 row items-center q-gutter-sm">
            <q-chip dense square color="white" text-color="grey-8" class="shadow-1">
              <q-icon name="tune" color="primary" class="q-mr-xs" />
              Options: {{ game.options?.length ?? 0 }}
            </q-chip>
            <q-chip v-if="yesNoOptions.length" dense square color="white" text-color="grey-8" class="shadow-1">
              <q-icon name="toggle_on" color="secondary" class="q-mr-xs" />
              Toggles: {{ yesNoOptions.length }}
            </q-chip>
            <q-chip v-if="choiceOptions.length" dense square color="white" text-color="grey-8" class="shadow-1">
              <q-icon name="list" color="secondary" class="q-mr-xs" />
              Lists: {{ choiceOptions.length }}
            </q-chip>
          </q-card-section>
        </q-card>

        <!-- Options Section -->
        <div class="q-mb-xl">
          <div class="row items-center q-mb-md q-gutter-x-sm">
            <q-icon name="tune" size="md" color="grey-8" />
            <h2 class="text-h4 q-my-none text-weight-medium">Game Options</h2>
          </div>

          <q-banner v-if="!hasOptions" rounded class="bg-blue-1 text-primary q-mb-lg shadow-1">
            <template #avatar>
              <q-icon name="info" />
            </template>
            No custom options configured for this game.
          </q-banner>

          <div v-else class="row q-col-gutter-lg">
            <!-- Yes/No Options -->
            <div v-if="yesNoOptions.length" class="col-12">
              <q-card flat bordered class="shadow-1">
                <q-card-section class="bg-grey-2 q-py-sm">
                  <div class="text-subtitle1 text-weight-bold text-grey-8">Binary Toggles</div>
                </q-card-section>
                <q-card-section class="q-pa-none">
                  <q-list separator>
                    <q-item v-for="option in yesNoOptions" :key="option.id" class="q-py-md">
                      <q-item-section avatar>
                        <q-icon name="check_circle" color="positive" size="sm" />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label class="text-weight-medium text-body1">{{ option.name }}</q-item-label>
                        <q-item-label v-if="hasAvailability(option)" caption>
                          <div class="row items-center q-gutter-x-xs text-warning">
                            <q-icon name="rule" />
                            <span>Has availability rules</span>
                          </div>
                        </q-item-label>
                      </q-item-section>
                      <q-item-section side v-if="hasAvailability(option)">
                        <q-expansion-item
                          dense
                          flat
                          label="View rules"
                          header-class="text-caption text-grey-7"
                        >
                          <div class="q-pa-sm bg-grey-1 rounded-borders q-mt-xs">
                            <div v-for="(grp, idx) in option.availability_groups" :key="grp.id" class="q-mb-xs">
                              <div class="text-grey-6 text-caption text-uppercase">Group #{{ idx+1 }}</div>
                              <div v-for="cond in grp.conditions" :key="cond.id" class="text-caption">
                                • {{ formatCondition(cond) }}
                              </div>
                            </div>
                          </div>
                        </q-expansion-item>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-card-section>
              </q-card>
            </div>

            <!-- Choice Options -->
            <div v-for="option in choiceOptions" :key="option.id" class="col-12 col-md-6">
              <q-card flat bordered class="full-height shadow-1">
                <q-card-section class="bg-grey-2 q-py-sm row items-center justify-between">
                  <div class="text-subtitle1 text-weight-bold text-grey-8">{{ option.name }}</div>
                  <q-chip dense color="primary" text-color="white">{{ option.choices?.length ?? 0 }} items</q-chip>
                </q-card-section>
                <q-card-section>
                  <div class="row q-col-gutter-sm">
                    <div v-for="choice in option.choices" :key="choice.id" class="col-auto">
                      <q-chip outline color="secondary" icon="radio_button_checked" size="sm">{{ choice.name }}</q-chip>
                    </div>
                  </div>

                  <div v-if="hasAvailability(option)" class="q-mt-lg">
                    <q-separator class="q-mb-sm" />
                    <div class="text-caption text-weight-bold text-warning row items-center q-gutter-x-xs q-mb-xs">
                      <q-icon name="rule" />
                      <span>AVAILABILITY RULES</span>
                    </div>
                    <div v-for="grp in option.availability_groups" :key="grp.id" class="bg-orange-1 q-pa-sm rounded-borders q-mb-xs">
                       <div v-for="cond in grp.conditions" :key="cond.id" class="text-caption text-grey-9">
                        {{ formatCondition(cond) }}
                      </div>
                    </div>
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </div>

        <!-- Result Configuration Section -->
        <div class="q-mb-xl">
          <div class="row items-center q-mb-md q-gutter-x-sm">
            <q-icon name="emoji_events" size="md" color="grey-8" />
            <h2 class="text-h4 q-my-none text-weight-medium">Result & Scoring</h2>
          </div>

          <q-card flat bordered class="shadow-2 overflow-hidden">
            <q-card-section class="q-pa-none">
              <ResultConfiguration
                :hasPoints="resultConfig.has_points"
                :startingPointSystemCode="resultConfig.starting_points_system_code"
                :startingPointSystemDescription="resultConfig.starting_points_system_description"
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
  </q-page>
</template>

<script setup lang="ts">
import { api } from 'boot/axios';
import { useRoute, useRouter } from 'vue-router';
import ResultConfiguration from 'components/game/ResultConfiguration.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { computed, ref } from 'vue';

const route = useRoute();
const router = useRouter();
const isLoading = ref(true);

const { data: game } = await api(`game/games-full/${route.params.id}`);
const {
  data: [resultConfig],
} = await api(`game/result-configs/?game=${route.params.id}`);
const { data: tieBreakers } = await api(
  `game/tie-breakers/?result_config=${resultConfig.id}`
);
const { data: factions } = await api(`game/factions/?game=${route.params.id}`);
const { data: platform } = await api(`game/platforms/${game.platform}`);

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
const hasOptions = computed(
  () => yesNoOptions.value.length > 0 || choiceOptions.value.length > 0
);

function hasAvailability(option: any): boolean {
  return (
    Array.isArray(option.availability_groups) &&
    option.availability_groups.length > 0
  );
}

function formatCondition(cond: any): string {
  const left = cond?.depends_on_option_name ?? '(Unknown option)';
  const notPrefix = cond?.negate ? 'NOT ' : '';

  // boolean condition
  if (cond?.expected_value === true || cond?.expected_value === false) {
    return `${notPrefix}${left} is ${cond.expected_value ? 'true' : 'false'}`;
  }

  // choice condition
  const choiceName = cond?.expected_choice_name ?? '(Unknown choice)';
  return `${notPrefix}${left} is "${choiceName}"`;
}
</script>

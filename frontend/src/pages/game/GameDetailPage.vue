<template>
  <q-page padding>
    <LoadingSpinner v-if="isLoading" />

    <div v-else class="row justify-center">
      <div class="col-12 col-md-10 col-lg-9">
        <q-card flat bordered class="shadow-2 overflow-hidden">
          <!-- Header -->
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

          <q-card-section class="q-pa-md bg-grey-1 row items-center justify-between border-bottom">
            <div class="row items-center q-gutter-sm">
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
              <q-separator vertical inset class="q-mx-xs" />
              <q-chip dense square color="white" text-color="grey-8" class="shadow-1">
                <q-icon name="groups" color="accent" class="q-mr-xs" />
                Players: {{ game.min_players }} - {{ game.max_players }}
              </q-chip>
            </div>

            <div class="row items-center">
              <div v-if="!(game.selectable ?? true)" class="row items-center text-negative bg-red-1 q-px-sm q-py-xs rounded-borders border-negative">
                <q-icon name="block" size="xs" class="q-mr-xs" />
                <span class="text-caption text-weight-bold">NOT SELECTABLE</span>
              </div>
              <div v-else class="row items-center text-grey-6 q-px-sm">
                <q-icon name="check" size="xs" class="q-mr-xs" />
                <span class="text-caption">Selectable</span>
              </div>
            </div>
          </q-card-section>

          <q-card-section class="q-pa-lg">
            <!-- Options Section -->
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

            <div v-else>
              <!-- Yes/No Options -->
              <div v-if="yesNoOptions.length" class="q-mb-lg">
                <div class="text-subtitle1 text-weight-bold text-grey-9 q-mb-sm uppercase-label">Binary Toggles</div>
                <div class="row q-col-gutter-md">
                  <div v-for="option in yesNoOptions" :key="option.id" class="col-12 col-sm-6 col-md-4">
                    <div class="option-item q-pa-md rounded-borders bg-white border-light full-height">
                      <div class="row items-center no-wrap">
                        <q-icon name="check_circle" color="positive" size="sm" class="q-mr-sm" />
                        <div class="text-weight-medium text-body1 text-grey-9 ellipsis">{{ option.name }}</div>
                      </div>
                      <div v-if="hasAvailability(option)" class="q-mt-xs">
                        <div class="row items-center q-gutter-x-xs text-orange-9 cursor-pointer" @click="toggleRules(option.id)">
                          <q-icon name="rule" size="xs" />
                          <span class="text-caption text-weight-medium">Has rules</span>
                          <q-icon :name="expandedRules[option.id] ? 'expand_less' : 'expand_more'" size="xs" />
                        </div>
                        <q-slide-transition>
                          <div v-if="expandedRules[option.id]" class="q-pa-sm bg-grey-1 rounded-borders q-mt-xs shadow-1 border-light">
                            <div v-for="grp in option.availability_groups" :key="grp.id" class="q-mb-xs">
                              <div v-for="cond in grp.conditions" :key="cond.id" class="text-caption text-grey-9">
                                • {{ formatCondition(cond) }}
                              </div>
                            </div>
                          </div>
                        </q-slide-transition>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Choice Options -->
              <div v-if="choiceOptions.length">
                <div class="text-subtitle1 text-weight-bold text-grey-9 q-mb-sm uppercase-label">Configurable Lists</div>
                <div class="row q-col-gutter-md">
                  <div v-for="option in choiceOptions" :key="option.id" class="col-12 col-md-6">
                    <div class="option-item q-pa-md rounded-borders bg-white border-light full-height">
                      <div class="row items-center q-mb-md">
                        <div class="text-weight-bold text-grey-9">{{ option.name }}</div>
                        <q-badge color="grey-7" class="q-ml-sm" size="xs" transparent>{{ option.choices?.length ?? 0 }}</q-badge>
                      </div>
                      <div class="column q-gutter-y-sm">
                        <div v-for="choice in option.choices" :key="choice.id" class="row items-center q-gutter-x-sm">
                          <q-icon name="radio_button_checked" color="secondary" size="xs" />
                          <div class="text-body2 text-grey-9">{{ choice.name }}</div>
                        </div>
                      </div>

                      <div v-if="hasAvailability(option)" class="q-mt-md">
                        <q-separator class="q-my-sm opacity-50" />
                        <div class="text-caption text-weight-bold text-orange-9 row items-center q-gutter-x-xs cursor-pointer" @click="toggleRules(option.id)">
                          <q-icon name="rule" size="xs" />
                          <span>RULES</span>
                          <q-icon :name="expandedRules[option.id] ? 'expand_less' : 'expand_more'" size="xs" />
                        </div>
                        <q-slide-transition>
                          <div v-if="expandedRules[option.id]" class="q-mt-xs">
                            <div v-for="grp in option.availability_groups" :key="grp.id">
                              <div v-for="cond in grp.conditions" :key="cond.id" class="text-caption text-grey-8">
                                • {{ formatCondition(cond) }}
                              </div>
                            </div>
                          </div>
                        </q-slide-transition>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </q-card-section>

          <q-separator />

          <!-- Result Configuration Section -->
          <q-card-section class="q-pa-lg">
            <div class="row items-center q-mb-md q-gutter-x-sm">
              <q-icon name="emoji_events" size="md" color="grey-8" />
              <h2 class="text-h4 q-my-none text-weight-medium">Result & Scoring</h2>
            </div>

            <div class="border-light rounded-borders overflow-hidden bg-grey-1">
              <ResultConfiguration
                :hasPoints="resultConfig.has_points"
                :startingPointSystemCode="resultConfig.starting_points_system_code"
                :startingPointSystemDescription="resultConfig.starting_points_system_description"
                :hasStartingPlayerOrder="resultConfig.has_starting_player_order"
                :isAsymmetric="resultConfig.is_asymmetric"
                :factions="factions"
                :winConditions="winConditions"
              />
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<style scoped>
.border-negative {
  border: 1px solid currentColor;
}
.border-light {
  border: 1px solid #e0e0e0;
}
.border-bottom {
  border-bottom: 1px solid #e0e0e0;
}
.uppercase-label {
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.75rem;
}
.option-item {
  transition: all 0.2s ease;
}
.option-item:hover {
  border-color: var(--q-primary);
  background-color: #fafafa;
}
</style>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';
import ResultConfiguration from 'components/game/ResultConfiguration.vue';
import KennerButton from 'components/base/KennerButton.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import { computed, ref } from 'vue';
import { fetchGameDetailBundle } from 'src/services/gameService';

const route = useRoute();
const router = useRouter();
const isLoading = ref(true);
const expandedRules = ref<Record<number, boolean>>({});

function toggleRules(id: number) {
  expandedRules.value[id] = !expandedRules.value[id];
}

const { game, platform, resultConfig, winConditions, factions } =
  await fetchGameDetailBundle(Number(route.params.id));

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

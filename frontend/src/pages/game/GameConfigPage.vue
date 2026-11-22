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
                <div class="row items-center q-gutter-x-sm q-mb-xs">
                  <q-badge color="white" text-color="primary" class="text-weight-bold">
                    Admin Configuration
                  </q-badge>
                </div>
                <div class="text-h5 text-weight-bold tracking-tight">
                  {{ game.name }}
                </div>
                <div class="text-subtitle2 opacity-80">{{ platform.name }}</div>
              </div>
              <div class="row q-gutter-sm">
                <KennerButton
                  unelevated
                  size="sm"
                  color="white"
                  text-color="primary"
                  icon="analytics"
                  label="View Stats"
                  @click="
                    router.push({ name: 'game-detail', params: { id: game.id } })
                  "
                />
                <KennerButton
                  unelevated
                  size="sm"
                  color="white"
                  text-color="primary"
                  icon="edit"
                  label="Edit Game"
                  @click="
                    router.push({ name: 'game-edit', params: { id: game.id } })
                  "
                />
              </div>
            </div>
          </q-card-section>

          <q-card-section
            class="q-pa-md bg-grey-1 row items-center justify-between border-bottom"
          >
            <div class="row items-center q-gutter-sm">
              <div class="stat-pill">
                {{ game.options?.length ?? 0 }} options
              </div>
              <div v-if="yesNoOptions.length" class="stat-pill">
                {{ yesNoOptions.length }} toggles
              </div>
              <div v-if="choiceOptions.length" class="stat-pill">
                {{ choiceOptions.length }} lists
              </div>
              <div class="stat-pill">
                {{ game.min_players }} - {{ game.max_players }} players
              </div>
            </div>

            <div class="row items-center">
              <div
                v-if="!(game.selectable ?? true)"
                class="row items-center text-negative bg-red-1 q-px-sm q-py-xs rounded-borders border-negative"
              >
                <q-icon name="block" size="xs" class="q-mr-xs" />
                <span class="text-caption text-weight-bold"
                  >NOT SELECTABLE</span
                >
              </div>
              <div v-else class="row items-center text-grey-6 q-px-sm">
                <q-icon name="check" size="xs" class="q-mr-xs" />
                <span class="text-caption">Selectable</span>
              </div>
            </div>
          </q-card-section>

          <q-card-section class="q-pa-lg">
            <!-- Options Section -->
            <h2 class="text-h6 q-my-none q-mb-md text-weight-bold">
              Game Options
            </h2>

            <q-banner
              v-if="!hasOptions"
              rounded
              class="bg-blue-1 text-primary q-mb-lg shadow-1"
            >
              <template #avatar>
                <q-icon name="info" />
              </template>
              No custom options configured for this game.
            </q-banner>

            <div v-else>
              <!-- Yes/No Options -->
              <div v-if="yesNoOptions.length" class="q-mb-lg">
                <div
                  class="text-subtitle1 text-weight-bold text-grey-9 q-mb-sm uppercase-label"
                >
                  Binary Toggles
                </div>
                <div class="row q-col-gutter-md">
                  <div
                    v-for="option in yesNoOptions"
                    :key="option.id"
                    class="col-12 col-sm-6 col-md-4"
                  >
                    <div
                      class="option-item q-pa-md rounded-borders bg-white border-light full-height"
                    >
                      <div class="row items-center no-wrap">
                        <q-icon
                          name="check_circle"
                          color="positive"
                          size="sm"
                          class="q-mr-sm"
                        />
                        <div
                          class="text-weight-medium text-body1 text-grey-9 ellipsis"
                        >
                          {{ option.name }}
                        </div>
                      </div>

                      <!-- Availability rules indicator / expansion -->
                      <div v-if="hasAvailability(option)" class="q-mt-sm">
                        <q-btn
                          flat
                          dense
                          no-caps
                          size="sm"
                          color="primary"
                          :icon="
                            expandedRules[option.id]
                              ? 'expand_less'
                              : 'expand_more'
                          "
                          :label="`Rules (${option.availability_groups.length})`"
                          @click="toggleRules(option.id)"
                        />

                        <q-slide-transition>
                          <div
                            v-show="expandedRules[option.id]"
                            class="q-mt-xs text-caption bg-grey-1 q-pa-sm rounded-borders"
                          >
                            <div class="text-weight-medium text-grey-8 q-mb-xs">
                              Available if ANY group matches:
                            </div>

                            <div
                              v-for="(
                                grp, gIdx
                              ) in option.availability_groups"
                              :key="grp.id"
                              class="q-mb-xs"
                            >
                              <span class="text-weight-bold text-grey-7"
                                >Group {{ gIdx + 1 }}:</span
                              >
                              <div
                                v-for="c in grp.conditions"
                                :key="c.id"
                                class="q-pl-sm text-grey-8"
                              >
                                &bull; {{ formatCondition(c) }}
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
                <div
                  class="text-subtitle1 text-weight-bold text-grey-9 q-mb-sm uppercase-label"
                >
                  Choice Selections
                </div>
                <div class="row q-col-gutter-md">
                  <div
                    v-for="option in choiceOptions"
                    :key="option.id"
                    class="col-12 col-md-6"
                  >
                    <q-card flat bordered class="rounded-borders bg-white">
                      <q-card-section class="q-pa-md bg-grey-1 border-bottom">
                        <div class="row items-center justify-between no-wrap">
                          <div class="row items-center no-wrap">
                            <q-icon
                              name="list"
                              color="primary"
                              size="sm"
                              class="q-mr-sm"
                            />
                            <div
                              class="text-weight-bold text-body1 text-grey-9 ellipsis"
                            >
                              {{ option.name }}
                            </div>
                          </div>
                          <q-badge color="grey-3" text-color="grey-8">
                            {{ option.choices?.length ?? 0 }} choices
                          </q-badge>
                        </div>

                        <!-- Availability rules indicator / expansion -->
                        <div v-if="hasAvailability(option)" class="q-mt-sm">
                          <q-btn
                            flat
                            dense
                            no-caps
                            size="sm"
                            color="primary"
                            :icon="
                              expandedRules[option.id]
                                ? 'expand_less'
                                : 'expand_more'
                            "
                            :label="`Rules (${option.availability_groups.length})`"
                            @click="toggleRules(option.id)"
                          />

                          <q-slide-transition>
                            <div
                              v-show="expandedRules[option.id]"
                              class="q-mt-xs text-caption bg-white q-pa-sm rounded-borders border-light"
                            >
                              <div
                                class="text-weight-medium text-grey-8 q-mb-xs"
                              >
                                Available if ANY group matches:
                              </div>

                              <div
                                v-for="(
                                  grp, gIdx
                                ) in option.availability_groups"
                                :key="grp.id"
                                class="q-mb-xs"
                              >
                                <span class="text-weight-bold text-grey-7"
                                  >Group {{ gIdx + 1 }}:</span
                                >
                                <div
                                  v-for="c in grp.conditions"
                                  :key="c.id"
                                  class="q-pl-sm text-grey-8"
                                >
                                  &bull; {{ formatCondition(c) }}
                                </div>
                              </div>
                            </div>
                          </q-slide-transition>
                        </div>
                      </q-card-section>

                      <q-list dense separator class="q-py-xs">
                        <q-item
                          v-for="choice in option.choices"
                          :key="choice.id"
                          class="q-py-sm"
                        >
                          <q-item-section avatar style="min-width: 32px">
                            <q-icon
                              name="radio_button_unchecked"
                              size="xs"
                              color="grey-5"
                            />
                          </q-item-section>
                          <q-item-section>
                            <q-item-label class="text-grey-9">{{
                              choice.name
                            }}</q-item-label>
                          </q-item-section>
                        </q-item>
                      </q-list>
                    </q-card>
                  </div>
                </div>
              </div>
            </div>
          </q-card-section>

          <q-separator />

          <!-- Result Configuration Section -->
          <q-card-section class="q-pa-lg">
            <h2 class="text-h6 q-my-none q-mb-md text-weight-bold">
              Result & Scoring
            </h2>

            <div class="border-light rounded-borders overflow-hidden bg-grey-1">
              <ResultConfiguration
                :hasPoints="resultConfig.has_points"
                :startingPointSystemCode="
                  resultConfig.starting_points_system_code
                "
                :startingPointSystemDescription="
                  resultConfig.starting_points_system_description
                "
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
  border: 1px solid var(--kenner-surface-strong);
}
.border-bottom {
  border-bottom: 1px solid var(--kenner-surface-strong);
}
.uppercase-label {
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.75rem;
}
.stat-pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(54, 64, 88, 0.06);
  color: var(--kenner-text-secondary);
  font-size: 12px;
  font-weight: 600;
}
.body--dark .stat-pill {
  background: var(--kenner-hover-bg);
}
</style>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';
import ResultConfiguration from 'components/game/ResultConfiguration.vue';
import KennerButton from 'components/base/KennerButton.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import { computed, ref, onMounted } from 'vue';
import { fetchGameDetailBundle } from 'src/services/gameService';

const route = useRoute();
const router = useRouter();
const isLoading = ref(true);
const expandedRules = ref<Record<number, boolean>>({});

function toggleRules(id: number) {
  expandedRules.value[id] = !expandedRules.value[id];
}

const gameData = ref<any>(null);

onMounted(async () => {
  try {
    const bundle = await fetchGameDetailBundle(Number(route.params.id));
    gameData.value = bundle;
  } finally {
    isLoading.value = false;
  }
});

const game = computed(() => gameData.value?.game || { options: [] });
const platform = computed(() => gameData.value?.platform || {});
const resultConfig = computed(() => gameData.value?.resultConfig || {});
const winConditions = computed(() => gameData.value?.winConditions || []);
const factions = computed(() => gameData.value?.factions || []);

// Filter yesNoOptions (those without choices)
const yesNoOptions = computed(() =>
  game.value.options?.filter((option: any) => !option.has_choices) || []
);

// Filter the choiceOptions (those with existing choices)
const choiceOptions = computed(() =>
  game.value.options?.filter((option: any) => option.has_choices) || []
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

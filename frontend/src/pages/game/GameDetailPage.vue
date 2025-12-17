<template>
  <div class="q-pa-md">
    <!-- Loading State -->
    <div v-if="isLoading" class="flex flex-center q-pa-xl">
      <q-spinner-puff color="primary" size="3em" />
    </div>

    <div v-else class="row justify-center">
      <div class="col-12">
        <!-- Header -->
        <q-card flat bordered class="q-mb-lg">
          <q-card-section class="q-pb-sm">
            <div class="row items-start justify-between q-col-gutter-md">
              <div class="col">
                <div class="text-h5 text-weight-medium ellipsis">
                  {{ game.name }}
                </div>
                <div class="text-caption text-grey-7 q-mt-xs">
                  Game overview
                </div>
              </div>

              <div class="col-auto">
                <q-chip
                  outline
                  color="primary"
                  text-color="primary"
                  icon="sports_esports"
                  class="q-px-md"
                >
                  {{ platform.name }}
                </q-chip>
              </div>
            </div>
          </q-card-section>

          <q-separator />

          <q-card-section class="q-pt-sm">
            <div class="row items-center q-gutter-sm">
              <q-chip dense square color="primary" text-color="white" icon="tune">
                Options: {{ game.options?.length ?? 0 }}
              </q-chip>
              <q-chip
                v-if="yesNoOptions.length"
                dense
                square
                outline
                color="secondary"
                text-color="secondary"
                icon="toggle_on"
              >
                Yes/No: {{ yesNoOptions.length }}
              </q-chip>
              <q-chip
                v-if="choiceOptions.length"
                dense
                square
                outline
                color="secondary"
                text-color="secondary"
                icon="list"
              >
                Choice: {{ choiceOptions.length }}
              </q-chip>
            </div>
          </q-card-section>
        </q-card>

        <!-- Options -->
        <q-card flat bordered class="q-mb-lg">
          <q-card-section class="row items-center justify-between q-pb-sm">
            <div class="row items-center q-gutter-sm">
              <q-icon name="tune" class="text-primary" />
              <div class="text-h6">Game Options</div>
            </div>
            <q-chip dense outline color="primary" text-color="primary" icon="rule">
              Settings
            </q-chip>
          </q-card-section>

          <q-separator />

          <q-card-section>
            <q-banner v-if="!hasOptions" rounded class="bg-blue-1 text-primary">
              <template #avatar>
                <q-icon name="info" class="text-primary" />
              </template>
              No options configured for this game.
            </q-banner>

            <div v-else class="row q-col-gutter-md">
              <!-- Enabled/Disabled Options Card -->
              <div v-if="yesNoOptions.length" class="col-12 col-sm-6 col-md-4">
                <q-card flat bordered class="full-height">
                  <q-card-section class="q-pb-sm">
                    <div class="row items-center justify-between">
                      <div class="row items-center q-gutter-sm">
                        <q-icon name="toggle_on" class="text-secondary" />
                        <div class="text-subtitle1 text-weight-medium">
                          Enabled / Disabled
                        </div>
                      </div>
                      <q-chip dense color="secondary" text-color="white" icon="done_all">
                        {{ yesNoOptions.length }}
                      </q-chip>
                    </div>
                    <div class="text-caption text-grey-7 q-mt-xs">
                      Boolean toggles
                    </div>
                  </q-card-section>

                  <q-separator />

                  <q-card-section class="q-pt-sm">
                    <q-list dense padding>
                      <q-item
                        v-for="option in yesNoOptions"
                        :key="option.id"
                        class="q-px-sm rounded-borders q-mb-xs"
                      >
                        <q-item-section avatar class="items-center" style="min-width: 28px;">
                          <q-icon name="check_circle" color="positive" size="sm" />
                        </q-item-section>

                        <q-item-section>
                          <q-item-label class="row items-center no-wrap">
                            <span class="ellipsis">{{ option.name }}</span>
                            <q-space />
                            <q-chip
                              v-if="hasAvailability(option)"
                              dense
                              outline
                              color="warning"
                              text-color="warning"
                              icon="rule"
                            >
                              Conditional
                            </q-chip>
                          </q-item-label>

                          <!-- Conditions -->
                          <div v-if="hasAvailability(option)" class="q-mt-xs">
                            <q-expansion-item
                              dense
                              switch-toggle-side
                              icon="rule"
                              label="Availability rules"
                              header-class="text-grey-8"
                              expand-separator
                            >
                              <div class="q-pl-md q-pr-sm q-pb-sm">
                                <div
                                  v-for="grp in option.availability_groups"
                                  :key="grp.id"
                                  class="q-mt-sm"
                                >
                                  <q-list dense class="rounded-borders bg-white">
                                    <q-item
                                      v-for="cond in grp.conditions"
                                      :key="cond.id"
                                      class="q-px-sm"
                                    >
                                      <q-item-section
                                        avatar
                                        class="items-center"
                                        style="min-width: 28px;"
                                      >
                                        <q-icon
                                          name="subdirectory_arrow_right"
                                          color="primary"
                                          size="xs"
                                        />
                                      </q-item-section>
                                      <q-item-section>
                                        <q-item-label>{{ formatCondition(cond) }}</q-item-label>
                                      </q-item-section>
                                    </q-item>
                                  </q-list>
                                </div>
                              </div>
                            </q-expansion-item>
                          </div>
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
                  <q-card-section class="q-pb-sm">
                    <div class="row items-center justify-between q-col-gutter-sm">
                      <div class="col text-subtitle1 text-weight-medium ellipsis">
                        {{ option.name }}
                      </div>
                      <div class="col-auto">
                        <q-chip dense color="primary" text-color="white" icon="list">
                          {{ option.choices?.length ?? 0 }}
                        </q-chip>
                      </div>
                    </div>

                    <div class="row items-center q-gutter-xs q-mt-xs">
                      <q-chip
                        v-if="hasAvailability(option)"
                        dense
                        outline
                        color="warning"
                        text-color="warning"
                        icon="rule"
                      >
                        Conditional
                      </q-chip>
                    </div>
                  </q-card-section>

                  <q-separator />

                  <q-card-section class="q-pt-sm">
                    <q-list dense padding>
                      <q-item
                        v-for="choice in option.choices"
                        :key="choice.id ?? choice.name"
                        class="q-px-sm rounded-borders q-mb-xs"
                      >
                        <q-item-section avatar class="items-center" style="min-width: 28px;">
                          <q-icon name="circle" color="secondary" size="6px" />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label class="ellipsis">{{ choice.name }}</q-item-label>
                        </q-item-section>
                      </q-item>
                    </q-list>

                    <!-- Conditions -->
                    <div v-if="hasAvailability(option)" class="q-mt-sm">
                      <q-expansion-item
                        dense
                        switch-toggle-side
                        icon="rule"
                        label="Availability rules"
                        header-class="text-grey-8"
                        expand-separator
                      >
                        <div class="q-pb-sm">
                          <div
                            v-for="(grp, grpIndex) in option.availability_groups"
                            :key="grp.id"
                            class="q-mt-sm"
                          >
                            <q-chip
                              dense
                              outline
                              color="primary"
                              text-color="primary"
                              icon="call_split"
                              class="q-mb-xs"
                            >
                              OR group #{{ grpIndex + 1 }}
                            </q-chip>

                            <q-list dense bordered class="rounded-borders bg-white">
                              <q-item
                                v-for="cond in grp.conditions"
                                :key="cond.id"
                                class="q-px-sm"
                              >
                                <q-item-section
                                  avatar
                                  class="items-center"
                                  style="min-width: 28px;"
                                >
                                  <q-icon
                                    name="subdirectory_arrow_right"
                                    color="primary"
                                    size="xs"
                                  />
                                </q-item-section>
                                <q-item-section>
                                  <q-item-label>{{ formatCondition(cond) }}</q-item-label>
                                </q-item-section>
                              </q-item>
                            </q-list>
                          </div>
                        </div>
                      </q-expansion-item>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- Result Configuration -->
        <q-card flat bordered>
          <q-card-section class="row items-center justify-between q-pb-sm">
            <div class="row items-center q-gutter-sm">
              <q-icon name="emoji_events" class="text-primary" />
              <div class="text-h6">Result Configuration</div>
            </div>
            <q-chip dense color="secondary" text-color="white" icon="emoji_events">
              Scoring
            </q-chip>
          </q-card-section>

          <q-separator />

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

function hasAvailability(option: any): boolean {
  return Array.isArray(option.availability_groups) && option.availability_groups.length > 0;
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

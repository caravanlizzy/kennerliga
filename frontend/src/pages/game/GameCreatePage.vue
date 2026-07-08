<template>
  <q-page padding>
    <div class="row justify-center">
      <div class="col-12 col-md-10 col-lg-8">
        <q-card flat bordered class="q-pa-lg shadow-2">
          <div class="row items-center q-mb-lg q-gutter-x-sm">
            <q-icon
              name="add_circle"
              size="md"
              color="primary"
            />
            <h1 class="text-h4 q-my-none text-weight-bold">New Game</h1>
          </div>

          <q-form
            @submit.prevent="onSubmit"
            @keydown.enter.stop.prevent
            class="q-gutter-y-lg"
          >
            <!-- Basic Information -->
            <section>
              <div class="text-h6 q-mb-md text-grey-8">Basic Information</div>
              <div class="row q-col-gutter-md">
                <div class="col-12 col-sm-6">
                  <KennerInput
                    label="Game name"
                    v-model="name"
                    :rules="[(val: string) => !!val || 'Please enter a game name']"
                  />
                </div>
                <div class="col-12 col-sm-6">
                  <KennerInput
                    label="Short name"
                    v-model="shortName"
                    hint="Optional – used in compact views"
                  />
                </div>
                <div class="col-12">
                  <KennerSelect
                    label="Platform"
                    :options="platforms"
                    v-model="platform"
                    option-value="name"
                    option-label="name"
                    :rules="[(val: string) => !!val || 'Please select a platform']"
                  />
                </div>
                <div class="col-12 col-sm-4">
                  <q-checkbox v-model="selectable" label="Selectable" />
                </div>
                <div class="col-12 col-sm-4">
                  <KennerInput
                    label="Min Players"
                    v-model.number="minPlayers"
                    type="number"
                    :rules="[val => val !== null && val !== undefined || 'Required', val => val >= 1 || 'Min 1 player']"
                  />
                </div>
                <div class="col-12 col-sm-4">
                  <KennerInput
                    label="Max Players"
                    v-model.number="maxPlayers"
                    type="number"
                    :rules="[val => val !== null && val !== undefined || 'Required', val => val >= (minPlayers || 1) || 'Must be >= min players']"
                  />
                </div>
              </div>
            </section>

            <q-separator />

            <!-- Game options -->
            <section>
              <div class="row items-center justify-between q-mb-md">
                <div class="text-h6 text-grey-8">Game Options</div>
                <KennerButton
                  color="primary"
                  label="Add option"
                  icon="add"
                  unelevated
                  @click="addEmptyOption"
                />
              </div>

              <div
                v-if="!gameOptions.length"
                class="text-center q-pa-xl bg-grey-1 rounded-borders border-dashed"
              >
                <q-icon name="list" size="xl" color="grey-4" />
                <div class="text-grey-6 q-mt-sm">No options added yet.</div>
              </div>

              <div v-else class="column q-gutter-y-md">
                <div v-for="(opt, optIdx) in gameOptions" :key="opt.ref">
                  <q-card flat bordered class="option-card overflow-hidden">
                    <q-card-section
                      class="bg-grey-1 row items-center justify-between q-py-sm"
                    >
                      <div class="row items-center q-gutter-x-sm">
                        <div class="text-subtitle1 text-weight-bold">
                          #{{ optIdx + 1 }}
                        </div>
                        <KennerInput
                          v-model="opt.name"
                          placeholder="Option Name"
                          class="text-subtitle1 text-weight-medium"
                          input-class="q-px-sm"
                        />
                      </div>
                      <div class="row items-center q-gutter-x-xs">
                        <KennerButton
                          flat
                          round
                          dense
                          size="sm"
                          icon="arrow_upward"
                          :disable="optIdx === 0"
                          @click="moveOption(optIdx, 'up')"
                        />
                        <KennerButton
                          flat
                          round
                          dense
                          size="sm"
                          icon="arrow_downward"
                          :disable="optIdx === gameOptions.length - 1"
                          @click="moveOption(optIdx, 'down')"
                        />
                        <q-separator vertical class="q-mx-xs" />
                        <KennerButton
                          flat
                          round
                          dense
                          icon="delete"
                          color="negative"
                          @click="removeOption(opt.ref)"
                        />
                      </div>
                    </q-card-section>

                    <q-card-section class="q-pa-md">
                      <div class="row items-center q-mb-md">
                        <q-toggle
                          v-model="opt.has_choices"
                          label="Has choices"
                          color="primary"
                        />
                        <q-icon
                          name="help_outline"
                          size="xs"
                          color="grey-5"
                          class="q-ml-xs"
                        >
                          <KennerTooltip
                            >If enabled, players can choose from a list. If
                            disabled, it's a simple toggle.</KennerTooltip
                          >
                        </q-icon>
                      </div>

                      <!-- Choices -->
                      <div v-if="opt.has_choices" class="q-pl-md q-border-l">
                        <div class="row items-center justify-between q-mb-sm">
                          <div class="text-subtitle2 text-grey-7">Choices</div>
                          <KennerButton
                            flat
                            dense
                            size="sm"
                            icon="add"
                            label="Add choice"
                            color="primary"
                            @click="addChoice(opt.ref)"
                          />
                        </div>

                        <div
                          v-if="!opt.choices.length"
                          class="text-caption text-grey-5 q-mb-md"
                        >
                          No choices defined.
                        </div>
                        <div
                          v-for="(ch, chIdx) in opt.choices"
                          :key="ch.ref"
                          class="row items-center q-col-gutter-x-sm q-mb-xs"
                        >
                          <div class="col-auto">
                            <div class="column">
                              <KennerButton
                                flat
                                round
                                dense
                                size="xs"
                                icon="keyboard_arrow_up"
                                :disable="chIdx === 0"
                                @click="moveChoice(opt.ref, chIdx, 'up')"
                              />
                              <KennerButton
                                flat
                                round
                                dense
                                size="xs"
                                icon="keyboard_arrow_down"
                                :disable="chIdx === opt.choices.length - 1"
                                @click="moveChoice(opt.ref, chIdx, 'down')"
                              />
                            </div>
                          </div>
                          <div class="col">
                            <KennerInput
                              v-model="ch.name"
                              placeholder="Choice name"
                            />
                          </div>
                          <div class="col-auto">
                            <KennerButton
                              flat
                              round
                              dense
                              icon="delete"
                              size="sm"
                              color="negative"
                              @click="removeChoice(opt.ref, ch.ref)"
                            />
                          </div>
                        </div>
                      </div>

                      <q-separator class="q-my-lg" />

                      <!-- Availability rules -->
                      <div>
                        <div class="row items-center justify-between q-mb-sm">
                          <div class="text-subtitle2 text-grey-7">
                            Availability Rules
                          </div>
                          <KennerButton
                            flat
                            dense
                            size="sm"
                            icon="add_rule"
                            label="Add condition group"
                            color="secondary"
                            @click="addAvailabilityGroup(opt.ref)"
                          />
                        </div>

                        <div
                          v-if="!opt.availability_groups.length"
                          class="text-caption text-grey-6 italic"
                        >
                          Always available.
                        </div>

                        <div class="column q-gutter-y-sm">
                          <div
                            v-for="(grp, grpIndex) in opt.availability_groups"
                            :key="grp.id"
                            class="q-pa-md bg-grey-1 rounded-borders border-light relative-position"
                          >
                            <div
                              class="row items-center justify-between q-mb-sm"
                            >
                              <div class="text-overline text-grey-7">
                                Group #{{ grpIndex + 1 }} (OR)
                              </div>
                              <div class="row items-center q-gutter-x-sm">
                                <KennerButton
                                  flat
                                  dense
                                  size="sm"
                                  icon="add"
                                  label="Condition"
                                  color="primary"
                                  @click="addCondition(opt.ref, grp.id)"
                                />
                                <KennerButton
                                  flat
                                  round
                                  dense
                                  size="xs"
                                  icon="delete"
                                  color="negative"
                                  @click="
                                    removeAvailabilityGroup(opt.ref, grp.id)
                                  "
                                />
                              </div>
                            </div>

                            <div
                              v-if="!grp.conditions.length"
                              class="text-caption text-grey-5"
                            >
                              No conditions in this group.
                            </div>

                            <div class="column q-gutter-y-xs">
                              <div
                                v-for="cond in grp.conditions"
                                :key="cond.id"
                                class="row items-center q-col-gutter-sm bg-white q-pa-sm rounded-borders shadow-1"
                              >
                                <div class="col-12 col-md-4">
                                  <KennerSelect
                                    dense
                                    outlined
                                    v-model="cond.depends_on_option_ref"
                                    :options="optionRefOptions(opt.ref)"
                                    option-value="value"
                                    option-label="label"
                                    emit-value
                                    map-options
                                    label="Depends on"
                                  />
                                </div>
                                <div class="col-6 col-md-3">
                                  <KennerSelect
                                    dense
                                    outlined
                                    v-model="cond.kind"
                                    :options="[
                                      { label: 'Value', value: 'value' },
                                      { label: 'Choice', value: 'choice' },
                                    ]"
                                    option-value="value"
                                    option-label="label"
                                    emit-value
                                    map-options
                                    label="Type"
                                    @update:model-value="
                                      onConditionKindChanged(cond)
                                    "
                                  />
                                </div>
                                <div class="col-6 col-md-4">
                                  <div v-if="cond.kind === 'value'">
                                    <KennerSelect
                                      dense
                                      outlined
                                      v-model="cond.expected_value"
                                      :options="[
                                        { label: 'Is True', value: true },
                                        { label: 'Is False', value: false },
                                      ]"
                                      option-value="value"
                                      option-label="label"
                                      emit-value
                                      map-options
                                      label="Expects"
                                    />
                                  </div>
                                  <div v-else>
                                    <KennerSelect
                                      dense
                                      outlined
                                      v-model="cond.expected_choice_ref"
                                      :options="
                                        choiceRefOptions(
                                          cond.depends_on_option_ref
                                        )
                                      "
                                      option-value="value"
                                      option-label="label"
                                      emit-value
                                      map-options
                                      label="Expects choice"
                                      :disable="!cond.depends_on_option_ref"
                                    />
                                  </div>
                                </div>
                                <div class="col-auto">
                                  <KennerButton
                                    flat
                                    round
                                    dense
                                    size="sm"
                                    icon="delete"
                                    color="grey-7"
                                    @click="
                                      removeCondition(opt.ref, grp.id, cond.id)
                                    "
                                  />
                                </div>
                                <div class="col-12 row items-center no-wrap">
                                  <q-toggle
                                    v-model="cond.negate"
                                    label="Negate (NOT)"
                                    dense
                                    color="red"
                                    class="text-caption"
                                  />
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </q-card-section>
                  </q-card>
                </div>
              </div>
            </section>

            <q-separator />

            <!-- Scoring Configuration -->
            <section>
              <div class="text-h6 q-mb-md text-grey-8">
                Scoring Configuration
              </div>
              <CreateResultConfig
                class="bg-grey-1 rounded-borders q-pa-sm"
                @update-result-config="updateResultConfig"
              />
            </section>

            <div class="row justify-end q-mt-xl">
              <KennerButton
                size="lg"
                type="submit"
                color="positive"
                label="Create Game"
                icon="save"
                unelevated
                class="q-px-xl"
              />
            </div>
          </q-form>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';
import KennerInput from 'components/base/KennerInput.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import { useRouter } from 'vue-router';
import CreateResultConfig from 'components/game/CreateResultConfig.vue';
import { TPlatform, TResultConfig } from 'src/types';
import { createResultConfigData } from 'src/services/gameService';
import { useGameForm } from 'src/composables/gameForm';

const router = useRouter();
const $q = useQuasar();

const { data: platforms } = await api('game/platforms/');

const {
  name,
  shortName,
  selectable,
  minPlayers,
  maxPlayers,
  platform,
  gameOptions,
  addEmptyOption,
  moveOption,
  removeOption,
  addChoice,
  moveChoice,
  removeChoice,
  addAvailabilityGroup,
  removeAvailabilityGroup,
  addCondition,
  removeCondition,
  onConditionKindChanged,
  optionRefOptions,
  choiceRefOptions,
  validateAvailabilityClientSide,
  buildPayload,
} = useGameForm();

let resultConfig: TResultConfig | undefined = undefined;
function updateResultConfig(newResultConfig: TResultConfig) {
  resultConfig = newResultConfig;
}

const onSubmit = async () => {
  try {
    // In create mode the KennerSelect binds a full TPlatform object.
    const selectedPlatform = platform.value as TPlatform | null;
    if (!selectedPlatform) return;

    const clientErrors = validateAvailabilityClientSide();
    if (clientErrors.length) {
      $q.notify({
        color: 'negative',
        textColor: 'white',
        icon: 'warning',
        message: clientErrors[0],
      });
      return;
    }

    const payload = buildPayload(selectedPlatform.id);

    const { data: game } = await api.post('/game/games-full/', payload);

    if (resultConfig !== undefined) {
      await createResultConfigData(game.id, resultConfig);
    } else {
      console.warn('Missing result config');
      return;
    }

    $q.notify({
      color: 'positive',
      textColor: 'white',
      icon: 'save',
      message: 'Saved',
    });

    await router.push({ name: 'games' });
  } catch (e) {
    console.error('Could not create game because', e);
    $q.notify({
      color: 'negative',
      textColor: 'white',
      icon: 'warning',
      message: 'Error creating game',
    });
  }
};
</script>

<style scoped>
.border-dashed {
  border: 2px dashed #e0e0e0;
}
.q-border-l {
  border-left: 2px solid #e0e0e0;
}
.italic {
  font-style: italic;
}
.border-light {
  border: 1px solid #f0f0f0;
}
.option-card {
  transition: transform 0.2s, shadow 0.2s;
}
.option-card:hover {
  border-color: var(--q-primary);
}
</style>

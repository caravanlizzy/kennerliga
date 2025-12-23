<template>
  <q-card flat bordered :class="['q-pa-md', isMobile ? '' : 'q-mt-md']">
    <p class="text-h5">New Game</p>

    <div class="q-py-md">
      <q-form
        @submit.prevent="onSubmit"
        @keydown.enter.stop.prevent
        class="q-gutter-md"
      >
        <!-- Game name -->
        <KennerInput
          class="max-w"
          label="Game name"
          v-model="name"
          :rules="[(val: string) => !!val || 'Please enter a game name']"
        />

        <KennerInput
          class="max-w"
          label="Short name"
          v-model="shortName"
          hint="Optional – used in compact / mobile views. Defaults to Game name."
        />

        <KennerSelect
          class="max-w"
          label="Platform"
          :options="platforms"
          v-model="platform"
          option-value="name"
          option-label="name"
          :rules="[(val: string) => !!val || 'Please select a platform']"
        />

        <!-- Game options -->
        <div class="q-mt-lg q-pa-md bg-grey-2 rounded-borders">
          <div class="row items-center justify-between q-mb-sm">
            <span class="text-h6">Game options</span>
            <KennerButton
              class="q-ml-lg"
              color="dark"
              label="Add option"
              icon="add"
              @click="addEmptyOption"
            />
          </div>

          <div
            v-if="!gameOptions.length"
            class="text-caption text-grey-7 q-pa-sm"
          >
            No options yet. Click
            <span class="text-weight-medium">Add option</span> to get started.
          </div>

          <div v-else class="row q-col-gutter-md">
            <div v-for="(opt, optIdx) in gameOptions" :key="opt.ref" class="col-12 col-sm-6 col-md-4">
              <q-card flat bordered>
                <q-card-section class="row items-center justify-between">
                  <div class="row items-center">
                    <div class="text-subtitle1">Option #{{ optIdx + 1 }}</div>
                    <div class="q-ml-sm row">
                      <q-btn
                        flat
                        dense
                        size="sm"
                        icon="arrow_upward"
                        :disable="optIdx === 0"
                        @click="moveOption(optIdx, 'up')"
                      />
                      <q-btn
                        flat
                        dense
                        size="sm"
                        icon="arrow_downward"
                        :disable="optIdx === gameOptions.length - 1"
                        @click="moveOption(optIdx, 'down')"
                      />
                    </div>
                  </div>
                  <q-btn flat dense icon="delete" color="negative" @click="removeOption(opt.ref)" />
                </q-card-section>

                <q-separator />

                <q-card-section class="q-gutter-sm">
                  <KennerInput label="Name" v-model="opt.name" />

                  <q-toggle v-model="opt.has_choices" label="Has choices" />

                  <!-- Choices -->
                  <div v-if="opt.has_choices" class="q-mt-sm">
                    <div class="row items-center justify-between q-mb-xs">
                      <div class="text-subtitle2">Choices</div>
                      <q-btn
                        flat
                        dense
                        icon="add"
                        label="Add choice"
                        color="primary"
                        @click="addChoice(opt.ref)"
                      />
                    </div>

                    <div v-if="!opt.choices.length" class="text-caption text-grey-7">
                      No choices yet.
                    </div>
                    <div v-for="(ch, chIdx) in opt.choices" :key="ch.ref" class="row items-center q-col-gutter-sm q-mb-sm">
                      <div class="col-auto column">
                        <q-btn
                          flat
                          dense
                          size="xs"
                          icon="keyboard_arrow_up"
                          :disable="chIdx === 0"
                          @click="moveChoice(opt.ref, chIdx, 'up')"
                        />
                        <q-btn
                          flat
                          dense
                          size="xs"
                          icon="keyboard_arrow_down"
                          :disable="chIdx === opt.choices.length - 1"
                          @click="moveChoice(opt.ref, chIdx, 'down')"
                        />
                      </div>
                      <div class="col">
                        <KennerInput dense v-model="ch.name" label="Choice name" />
                      </div>
                      <div class="col-auto">
                        <q-btn flat dense icon="delete" color="negative" @click="removeChoice(opt.ref, ch.ref)" />
                      </div>
                    </div>
                  </div>

                  <q-separator class="q-my-md" />

                  <!-- Availability rules -->
                  <div>
                    <div class="row items-center justify-between q-mb-xs">
                      <div class="text-subtitle2">Availability (OR groups)</div>
                      <q-btn
                        flat
                        dense
                        icon="add"
                        label="Add OR group"
                        color="primary"
                        @click="addAvailabilityGroup(opt.ref)"
                      />
                    </div>

                    <div
                      v-if="!opt.availability_groups.length"
                      class="text-caption text-grey-7"
                    >
                      No conditions. This option will be always available.
                    </div>

                    <div
                      v-for="(grp, grpIndex) in opt.availability_groups"
                      :key="grp.id"
                      class="q-mt-sm q-pa-sm bg-white rounded-borders"
                    >
                      <div class="row items-center justify-between q-mb-xs">
                        <div class="text-caption text-grey-8">
                          OR Group #{{ grpIndex + 1 }} (all conditions inside
                          must match)
                        </div>
                        <q-btn
                          flat
                          dense
                          icon="delete"
                          color="negative"
                          @click="removeAvailabilityGroup(opt.ref, grp.id)"
                        />
                      </div>

                      <div class="row items-center justify-between q-mb-xs">
                        <div class="text-subtitle2">Conditions (AND)</div>
                        <q-btn
                          flat
                          dense
                          icon="add"
                          label="Add condition"
                          color="primary"
                          @click="addCondition(opt.ref, grp.id)"
                        />
                      </div>

                      <div
                        v-if="!grp.conditions.length"
                        class="text-caption text-grey-7"
                      >
                        No conditions in this group yet.
                      </div>

                      <div
                        v-for="cond in grp.conditions"
                        :key="cond.id"
                        class="q-mt-sm q-pa-sm bg-grey-1 rounded-borders"
                      >
                        <div class="row items-start q-col-gutter-sm">
                          <div class="col-12 col-md-6">
                            <KennerSelect
                              dense
                              outlined
                              v-model="cond.depends_on_option_ref"
                              :options="optionRefOptions(opt.ref)"
                              option-value="value"
                              option-label="label"
                              emit-value
                              map-options
                              label="Depends on option"
                            />
                          </div>

                          <div class="col-12 col-md-3">
                            <KennerSelect
                              dense
                              outlined
                              v-model="cond.kind"
                              :options="[
                                { label: 'Boolean value', value: 'value' },
                                { label: 'Specific choice', value: 'choice' },
                              ]"
                              option-value="value"
                              option-label="label"
                              emit-value
                              map-options
                              label="Condition type"
                              @update:model-value="onConditionKindChanged(cond)"
                            />
                          </div>

                          <div class="col-12 col-md-3">
                            <q-toggle v-model="cond.negate" label="NOT" />
                          </div>

                          <div class="col-12" v-if="cond.kind === 'value'">
                            <KennerSelect
                              dense
                              outlined
                              v-model="cond.expected_value"
                              :options="[
                                { label: 'true', value: true },
                                { label: 'false', value: false },
                              ]"
                              option-value="value"
                              option-label="label"
                              emit-value
                              map-options
                              label="Expected value"
                            />
                          </div>

                          <div class="col-12" v-else>
                            <KennerSelect
                              dense
                              outlined
                              v-model="cond.expected_choice_ref"
                              :options="
                                choiceRefOptions(cond.depends_on_option_ref)
                              "
                              option-value="value"
                              option-label="label"
                              emit-value
                              map-options
                              label="Expected choice"
                              :disable="!cond.depends_on_option_ref"
                              hint="Select the choice from the referenced option"
                            />
                          </div>

                          <div class="col-12 row justify-end">
                            <q-btn
                              flat
                              dense
                              icon="delete"
                              color="negative"
                              label="Remove condition"
                              @click="removeCondition(opt.ref, grp.id, cond.id)"
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </div>

        <CreateResultConfig
          class="q-mt-md"
          @update-result-config="updateResultConfig"
        />

        <KennerButton
          class="q-my-xl"
          type="submit"
          color="positive"
          label="Save"
          icon="save"
        />
      </q-form>
    </div>
  </q-card>
</template>

<script setup lang="ts">
import { Ref, ref } from 'vue';
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';
import KennerInput from 'components/base/KennerInput.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { useRouter } from 'vue-router';
import CreateResultConfig from 'components/game/CreateResultConfig.vue';
import { TPlatform } from 'src/models/gameModels';
import { TResultConfig } from 'src/types';
import { createResultConfigData } from 'src/services/gameService';
import { useResponsive } from 'src/composables/responsive';

type ConditionKind = 'value' | 'choice';

type UiChoice = {
  ref: string; // client-only ref (string!)
  name: string;
  order: number;
};

type UiCondition = {
  id: string;
  depends_on_option_ref: string | null;
  kind: ConditionKind;
  expected_value: boolean | null;
  expected_choice_ref: string | null;
  negate: boolean;
};

type UiGroup = {
  id: string;
  conditions: UiCondition[];
};

type UiOption = {
  ref: string; // client-only ref (string!)
  name: string;
  order: number;
  has_choices: boolean;
  choices: UiChoice[];
  availability_groups: UiGroup[];
};

const router = useRouter();
const $q = useQuasar();
const { isMobile } = useResponsive();

const { data: platforms } = await api('game/platforms/');

const name = ref('');
const shortName = ref('');
const platform: Ref<TPlatform | undefined> = ref(undefined);

let resultConfig: TResultConfig | undefined = undefined;
function updateResultConfig(newResultConfig: TResultConfig) {
  resultConfig = newResultConfig;
}

/**
 * IMPORTANT: this MUST generate a unique string every time.
 * Using crypto.randomUUID() avoids the "duplicate key" issue when adding quickly.
 */
function newRef(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    // @ts-expect-error TS lib may not include randomUUID depending on config
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

const gameOptions = ref<UiOption[]>([]);

function addEmptyOption(): void {
  const nextOrder = (gameOptions.value.length + 1) * 10;
  gameOptions.value.push({
    ref: newRef(),
    name: '',
    order: nextOrder,
    has_choices: false,
    choices: [],
    availability_groups: [],
  });
}

function resortOrders() {
  gameOptions.value.forEach((opt, idx) => {
    opt.order = (idx + 1) * 10;
    opt.choices.forEach((ch, cIdx) => {
      ch.order = (cIdx + 1) * 10;
    });
  });
}

function moveOption(index: number, direction: 'up' | 'down') {
  const newIndex = direction === 'up' ? index - 1 : index + 1;
  if (newIndex < 0 || newIndex >= gameOptions.value.length) return;
  const temp = gameOptions.value[index];
  gameOptions.value[index] = gameOptions.value[newIndex];
  gameOptions.value[newIndex] = temp;
  resortOrders();
}

function removeOption(optionRef: string) {
  gameOptions.value = gameOptions.value.filter((o) => o.ref !== optionRef);
}

function addChoice(optionRef: string) {
  const opt = gameOptions.value.find((o) => o.ref === optionRef);
  if (!opt) return;
  const nextOrder = (opt.choices.length + 1) * 10;
  opt.choices.push({
    ref: newRef(),
    name: '',
    order: nextOrder,
  });
}

function moveChoice(optionRef: string, choiceIndex: number, direction: 'up' | 'down') {
  const opt = gameOptions.value.find((o) => o.ref === optionRef);
  if (!opt) return;
  const newIndex = direction === 'up' ? choiceIndex - 1 : choiceIndex + 1;
  if (newIndex < 0 || newIndex >= opt.choices.length) return;
  const temp = opt.choices[choiceIndex];
  opt.choices[choiceIndex] = opt.choices[newIndex];
  opt.choices[newIndex] = temp;
  resortOrders();
}

function removeChoice(optionRef: string, choiceRef: string) {
  const opt = gameOptions.value.find((o) => o.ref === optionRef);
  if (!opt) return;
  opt.choices = opt.choices.filter((c) => c.ref !== choiceRef);

  // If any condition referenced that choice, clear it
  for (const grp of opt.availability_groups) {
    for (const cond of grp.conditions) {
      if (cond.expected_choice_ref === choiceRef) {
        cond.expected_choice_ref = null;
      }
    }
  }
}

function addAvailabilityGroup(optionRef: string) {
  const opt = gameOptions.value.find((o) => o.ref === optionRef);
  if (!opt) return;
  opt.availability_groups.push({
    id: newRef(),
    conditions: [],
  });
}

function removeAvailabilityGroup(optionRef: string, groupId: string) {
  const opt = gameOptions.value.find((o) => o.ref === optionRef);
  if (!opt) return;
  opt.availability_groups = opt.availability_groups.filter(
    (g) => g.id !== groupId
  );
}

function addCondition(optionRef: string, groupId: string) {
  const opt = gameOptions.value.find((o) => o.ref === optionRef);
  if (!opt) return;
  const grp = opt.availability_groups.find((g) => g.id === groupId);
  if (!grp) return;

  grp.conditions.push({
    id: newRef(),
    depends_on_option_ref: null,
    kind: 'value',
    expected_value: true,
    expected_choice_ref: null,
    negate: false,
  });
}

function removeCondition(
  optionRef: string,
  groupId: string,
  conditionId: string
) {
  const opt = gameOptions.value.find((o) => o.ref === optionRef);
  if (!opt) return;
  const grp = opt.availability_groups.find((g) => g.id === groupId);
  if (!grp) return;
  grp.conditions = grp.conditions.filter((c) => c.id !== conditionId);
}

function onConditionKindChanged(cond: UiCondition) {
  if (cond.kind === 'value') {
    cond.expected_choice_ref = null;
    if (cond.expected_value === null) cond.expected_value = true;
  } else {
    cond.expected_value = null;
    cond.expected_choice_ref = null;
  }
}

function optionRefOptions(currentOptionRef: string) {
  // Exclude current option to avoid self-dependency
  return gameOptions.value
    .filter((o) => o.ref !== currentOptionRef)
    .map((o) => ({
      label: o.name?.trim()
        ? o.name
        : `(Unnamed option ${String(o.ref).slice(0, 6)})`,
      value: o.ref,
    }));
}

function choiceRefOptions(dependsOnOptionRef: string | null) {
  if (!dependsOnOptionRef) return [];
  const opt = gameOptions.value.find((o) => o.ref === dependsOnOptionRef);
  if (!opt) return [];
  return opt.choices.map((c) => ({
    label: c.name?.trim()
      ? c.name
      : `(Unnamed choice ${String(c.ref).slice(0, 6)})`,
    value: c.ref,
  }));
}

function validateAvailabilityClientSide(): string[] {
  const errors: string[] = [];

  // Ensure unique option refs + choice refs
  const optionRefs = new Set<string>();
  for (const opt of gameOptions.value) {
    if (optionRefs.has(opt.ref))
      errors.push(`Duplicate option ref: ${opt.ref}`);
    optionRefs.add(opt.ref);

    const choiceRefs = new Set<string>();
    for (const ch of opt.choices) {
      if (choiceRefs.has(ch.ref))
        errors.push(`Duplicate choice ref in option "${opt.name}": ${ch.ref}`);
      choiceRefs.add(ch.ref);
    }
  }

  // Validate conditions
  for (const opt of gameOptions.value) {
    for (const grp of opt.availability_groups) {
      for (const cond of grp.conditions) {
        if (!cond.depends_on_option_ref) {
          errors.push(
            `Option "${
              opt.name || '(unnamed)'
            }" has a condition missing "Depends on option".`
          );
          continue;
        }
        if (!optionRefs.has(cond.depends_on_option_ref)) {
          errors.push(
            `Condition depends_on_option_ref "${cond.depends_on_option_ref}" does not exist.`
          );
          continue;
        }

        if (cond.kind === 'value') {
          if (cond.expected_value === null)
            errors.push(`A boolean condition is missing expected_value.`);
        } else {
          if (!cond.expected_choice_ref)
            errors.push(`A choice condition is missing expected_choice_ref.`);
        }
      }
    }
  }

  return errors;
}

const onSubmit = async () => {
  try {
    if (!platform.value) return;

    const effectiveShortName =
      shortName.value.trim() !== '' ? shortName.value.trim() : name.value;

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

    const payload = {
      name: name.value,
      short_name: effectiveShortName,
      platform: platform.value.id,
      options: gameOptions.value.map((opt) => ({
        ref: opt.ref,
        name: opt.name,
        order: opt.order,
        has_choices: opt.has_choices,
        choices: opt.choices.map((ch) => ({
          ref: ch.ref,
          name: ch.name,
          order: ch.order,
        })),
        availability_groups: opt.availability_groups.map((grp) => ({
          conditions: grp.conditions.map((cond) => ({
            depends_on_option_ref: cond.depends_on_option_ref,
            negate: !!cond.negate,
            expected_value: cond.kind === 'value' ? cond.expected_value : null,
            expected_choice_ref:
              cond.kind === 'choice' ? cond.expected_choice_ref : null,
          })),
        })),
      })),
    };

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
.max-w {
  max-width: 300px;
}
</style>

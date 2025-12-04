<template>
  <div class="q-pa-md">
    <p class="text-h5">New Game</p>

    <div class="q-py-md">
      <q-form
        @submit.prevent="onSubmit"
        @keydown.enter.stop.prevent
        class="q-gutter-md"
      >
        <KennerInput
          class="max-w"
          label="Game name"
          v-model="name"
          :rules="[(val: string) => !!val || 'Please enter a game name']"
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
              color="primary"
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
            <div
              v-for="gameOption of gameOptions"
              :key="gameOption.id"
              class="col-12 col-sm-6 col-md-4"
            >
              <GameOption :gameOption="gameOption" />
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
          push
          color="positive"
          label="Save"
          icon="save"
        />
      </q-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { provide, Ref, ref } from 'vue';
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';
import KennerInput from 'components/base/KennerInput.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { TPlatform } from 'src/models/gameModels';
import GameOption from 'components/game/GameOptionCreate.vue';
import { useItemList } from 'src/composables/itemList';
import { useRouter } from 'vue-router';
import CreateResultConfig from 'components/game/CreateResultConfig.vue';
import { createRandomId } from 'src/helpers';
import { TGameOption, TResultConfig } from 'src/types';
import { createResultConfigData } from 'src/services/gameService';

const router = useRouter();
const $q = useQuasar();

const { data: platforms } = await api('game/platforms/');

const useGameOptions = useItemList<TGameOption>();
const { addItem: addOption, items: gameOptions } = useGameOptions;
provide('useGameOptions', useGameOptions);

const name = ref('');
const platform: Ref<TPlatform | undefined> = ref(undefined);

let resultConfig: TResultConfig | undefined = undefined;

function updateResultConfig(newResultConfig: TResultConfig) {
  resultConfig = newResultConfig;
}

function addEmptyOption(): void {
  const emptyOption: TGameOption = {
    title: '',
    hasChoices: false,
    id: createRandomId(),
    choices: [],
  };
  addOption(emptyOption, { prepend: true });
}

const onSubmit = async () => {
  try {
    if (!platform.value) return;

    const payload = {
      name: name.value,
      platform: platform.value.id,
      options: gameOptions.value.map((option) => ({
        name: option.title,
        has_choices: option.hasChoices,
        // keep your existing keys as-is:
        only_if_option: option.onlyIfOption || null,
        only_if_choice: option.onlyIfChoice || null,
        only_if_value: option.onlyIfValue ?? null,
        choices: option.choices.map((choice) => ({ name: choice.name })),
      })),
    };

    const { data: game } = await api.post('/game/games-full/', payload);

    if (resultConfig !== undefined) {
      await createResultConfigData(game.id, resultConfig); // keep this separate for now
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

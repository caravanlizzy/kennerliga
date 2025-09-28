<template>
  <div>
    <div class="column justify-center">
      <q-input
        v-model="filter"
        label="Spiel"
        outlined
        dense
        clearable
        class="rounded-borders col-grow"
      >
        <template v-slot:append>
          <q-icon name="search" />
        </template>
      </q-input>

      <q-btn-group spread outline push square>
        <q-btn
          v-for="p in platforms || []"
          :key="p.id"
          :color="platform?.id === p.id ? 'primary' : 'white'"
          :text-color="getPlatformColor(p.name).color"
          @click="platform = platform?.id === p.id ? null : p"
        >
          {{ p.name.length > 10 ? p.name.slice(0,11) : p.name }}
        </q-btn>
      </q-btn-group>
    </div>

    <div
      class="row q-pt-md justify-center"
      style="max-height: 220px; overflow-y: auto"
    >
      <q-card
        v-for="game in filteredGames"
        :key="game.id"
        @click="setGameInformation(game)"
        flat
        bordered
        square
        clickable
        class="cursor-pointer text-center q-pa-sm transition-all"
        style="width: 130px"
        :class="[
          game.id === gameSelection.game.id
            ? 'bg-primary text-white shadow-8'
            : 'bg-grey-3 text-dark shadow-2 hover-bg-grey-4 hover-shadow-6',
        ]"
      >
        <q-card-section class="q-pa-sm">
          <div class="text-body2 text-weight-bold ellipsis">
            {{
              game.name.length > 13 ? game.name.slice(0, 12) + '…' : game.name
            }}
          </div>

          <!-- Platform badge -->
          <q-chip
            dense
            square
            outline
            class="q-mt-xs"
            :color="getPlatformColor(getPlatformName(game.platform)).color"
            :text-color="getPlatformColor(getPlatformName(game.platform)).text"
          >
            {{ getPlatformName(game.platform).split('.')[0] }}
          </q-chip>
        </q-card-section>
      </q-card>
    </div>

    <div v-if="isLoading">
      <q-spinner-orbit size="xl" />
    </div>
    <q-card v-else-if="gameInformation.game" flat class="q-pa-md q-my-md">
      <!-- Game title -->
      <q-card-section>
        <div class="text-h6 text-weight-bold">
          {{ gameInformation.game.name }}
        </div>
      </q-card-section>

      <!-- No options -->
      <q-card-section v-if="!gameInformation.options.length">
        <div class="text-italic text-grey">
          This game has no additional settings
        </div>
      </q-card-section>

      <!-- With options -->
      <q-card-section v-else>
        <div class="text-subtitle2 text-primary q-mb-md">Settings</div>

        <!-- Choices -->
        <div
          v-if="gameInformation.options.some((o) => o.has_choices)"
          class="q-mb-md"
        >
          <div class="row q-col-gutter-md">
            <div
              v-for="option in gameInformation.options.filter(
                (o) => o.has_choices
              )"
              :key="option.id"
              class="col-12 col-sm-6 col-md-4"
            >
              <KennerSelect
                :options="findChoicesByOption(option.id)"
                :label="option.name"
                option-label="name"
                dense
                outlined
                v-model="
                  gameSelection.selectedOptions.find((o) => o.id == option.id)
                    .choice
                "
                class="full-width"
              />
            </div>
          </div>
        </div>

        <!-- Toggles -->
        <div v-if="gameInformation.options.some((o) => !o.has_choices)">
          <div class="row q-col-gutter-sm">
            <q-toggle
              v-for="option in gameInformation.options.filter(
                (o) => !o.has_choices
              )"
              :key="option.id"
              v-model="findSelectedOption(option.id).value"
              :label="option.name"
              dense
              color="secondary"
              class="col-auto"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import { h, onMounted, watch } from 'vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import { useGameSelection } from 'src/composables/gameSelection';
import { useLeagueStore } from 'stores/leagueStore';
import { storeToRefs } from 'pinia';
import { useActionBar } from 'src/composables/actionBar';

const { leagueId } = storeToRefs(useLeagueStore());

const {
  gameInformation,
  gameSelection,
  isLoading,
  setGameInformation,
  findChoicesByOption,
  findSelectedOption,
  submitGame,
  platform,
  filter,
  platforms,
  filteredGames,
  loadPlatformsAndGames,
} = useGameSelection(leagueId);

const emit = defineEmits(['submit-success']);

const handleSubmit = async () => {
  try {
    await submitGame();
    emit('submit-success');
  } catch (error) {
    console.error('Error submitting game:', error);
  }
};

const { setActions, setLeadText, setSubject } = useActionBar();

setActions([
  { name: 'Confirm', callback: handleSubmit, buttonVariant: 'positive', buttonFilled: true },
]);
setLeadText(() => h('div', 'Confirm your game selection'));
watch(gameSelection, (newVal) => {
  if (newVal.game) {
    setSubject(newVal.game.name);
  }
});

function getPlatformName(platformId: number | string): string {
  const platformObj = platforms.value.find((p) => p.id === platformId);
  return platformObj?.name ?? `ID: ${platformId}`;
}

function getPlatformColor(name: string): { color: string; text: string } {
  switch (name.toLowerCase()) {
    case 'boardgamers.space':
      return { color: 'deep-purple-3', text: 'white' };
    case 'yucata':
      return { color: 'blue-5', text: 'white' };
    case 'bga':
      return { color: 'green-5', text: 'white' };
    default:
      return { color: 'grey-3', text: 'dark' };
  }
}

onMounted(loadPlatformsAndGames);
</script>

<style lang="scss">
.select-width {
  width: 120px;
}
</style>

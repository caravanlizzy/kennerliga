<template>
  <div>
    <!-- FILTER BAR -->
    <div class="q-pa-sm q-mb-md bg-grey-2 rounded-borders">
      <div class="row items-center q-gutter-sm q-mb-sm">
        <q-icon name="tune" size="18px" class="text-grey-7" />
        <div class="text-caption text-uppercase text-grey-7">Filter</div>
      </div>

      <div class="row q-col-gutter-md items-start">
        <!-- Search -->
        <div class="col-12 col-md-6">
          <q-input
            v-model="filter"
            label="Spiel"
            outlined
            dense
            clearable
            class="rounded-borders"
          >
            <template #append>
              <q-icon name="search" />
            </template>
          </q-input>
        </div>

        <!-- Platform multi-select chips -->
        <div class="col-12 col-md-6">
          <div class="text-caption text-grey-7 q-mb-xs">Platform</div>
          <div class="row items-center q-gutter-xs">
            <q-chip
              v-for="p in platforms || []"
              :key="p.id"
              clickable
              :outline="!isPlatformSelected(p.id)"
              :color="getPlatformColor(p.name).color"
              :text-color="isPlatformSelected(p.id) ? 'white' : getPlatformColor(p.name).color"
              :style="!isPlatformSelected(p.id) ? 'background-color: white' : ''"
              @click="togglePlatform(p.id)"
            >
              <q-icon name="sports_esports" size="16px" class="q-mr-xs" />
              {{ shortPlatformLabel(p.name) }}
            </q-chip>
          </div>
        </div>
      </div>
    </div>

    <!-- GAME GRID -->
    <div
      class="row q-pt-md justify-center"
      style="max-height: 220px; overflow-y: auto"
    >
      <q-card
        v-for="game in displayedGames"
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
            : 'sandy-background text-dark shadow-2 hover-bg-grey-4 hover-shadow-6',
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

    <!-- DETAILS -->
    <div v-if="isLoading">
      <q-spinner-orbit size="xl" />
    </div>
    <q-card v-else-if="gameInformation.game" flat class="q-pa-md q-my-md">
      <q-card-section>
        <div class="text-h6 text-weight-bold">
          {{ gameInformation.game.name }}
        </div>
      </q-card-section>

      <q-card-section v-if="!gameInformation.options.length">
        <div class="text-italic text-grey">
          This game has no additional settings
        </div>
      </q-card-section>

      <q-card-section v-else>
        <div class="text-subtitle2 text-primary q-mb-md">Settings</div>

        <!-- Choices -->
        <div
          v-if="gameInformation.options.some((o) => o.has_choices)"
          class="q-mb-md"
        >
          <div class="row q-col-gutter-md">
            <div
              v-for="option in gameInformation.options.filter((o) => o.has_choices)"
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
                  gameSelection.selectedOptions.find((o) => o.id == option.id).choice
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
              v-for="option in gameInformation.options.filter((o) => !o.has_choices)"
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
import { h, onMounted, watch, computed, ref } from 'vue';
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
  filter,
  platforms,
  filteredGames,
  loadPlatformsAndGames,
} = useGameSelection(leagueId);

const selectedPlatforms = ref<Set<number>>(new Set());

const togglePlatform = (id: number) => {
  const s = new Set(selectedPlatforms.value);
  if (s.has(id)) s.delete(id);
  else s.add(id);
  selectedPlatforms.value = s;
};

const isPlatformSelected = (id: number) => selectedPlatforms.value.has(id);

// Final games displayed = composable's filteredGames (by name, etc.) AND our platform set
const displayedGames = computed(() => {
  const base = filteredGames.value || [];
  if (selectedPlatforms.value.size === 0) return base; // no platform filter = all
  return base.filter((g: any) => selectedPlatforms.value.has(g.platform));
});

// ---- actions / header wiring ----
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
setActions([{ name: 'Confirm', callback: handleSubmit, buttonVariant: 'secondary' }]);
setLeadText(() => h('div', 'Confirm your game selection'));
watch(gameSelection, (newVal) => {
  if (newVal.game) setSubject(newVal.game.name);
});

// ---- helpers ----
function getPlatformName(platformId: number | string): string {
  const platformObj = platforms.value.find((p: any) => p.id === platformId);
  return platformObj?.name ?? `ID: ${platformId}`;
}

function getPlatformColor(name: string): { color: string; text: string } {
  switch ((name || '').toLowerCase()) {
    case 'boardgamers.space':
      return { color: 'deep-purple-3', text: 'white' };
    case 'yucata':
      return { color: 'blue-5', text: 'white' };
    case 'bga':
      return { color: 'green-5', text: 'white' };
    default:
      return { color: 'grey-3', text: 'white' };
  }
}

function shortPlatformLabel(name: string): string {
  return name.length > 14 ? name.slice(0, 13) + '…' : name;
}

onMounted(loadPlatformsAndGames);
</script>

<template>
  <div class="row q-col-gutter-lg">
    <!-- LEFT: FILTER + GRID -->
    <div class="selector col-12 col-md-6">
      <!-- FILTER CARD -->
      <q-card flat bordered class="q-pa-md rounded-borders">
        <div class="row items-center q-gutter-sm q-mb-sm">
          <q-icon name="tune" size="18px" class="text-grey-7" />
          <div class="text-caption text-uppercase text-grey-7">Filters</div>
        </div>

        <div class="row q-col-gutter-md items-start">
          <!-- Search -->
          <div class="col-12 col-md-6">
            <q-input
              v-model="filter"
              label="Game"
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
                :text-color="
                  isPlatformSelected(p.id)
                    ? 'white'
                    : getPlatformColor(p.name).color
                "
                :style="
                  !isPlatformSelected(p.id) ? 'background-color: white' : ''
                "
                @click="togglePlatform(p.id)"
              >
                <q-icon name="sports_esports" size="16px" class="q-mr-xs" />
                {{ shortPlatformLabel(p.name) }}
              </q-chip>
            </div>
          </div>
        </div>
      </q-card>

      <!-- GAME GRID CARD -->
      <q-card flat bordered class="q-pa-sm q-mt-md rounded-borders">
        <div class="row items-center q-gutter-sm q-px-sm q-pt-sm q-pb-xs">
          <q-icon name="grid_view" size="16px" class="text-grey-7" />
          <div class="text-caption text-uppercase text-grey-7">
            Games ({{ displayedGames.length }})
          </div>
        </div>

        <div class="game-grid">
          <!-- Empty state -->
          <q-banner
            v-if="displayedGames.length === 0"
            class="bg-grey-2 text-grey-8 rounded-borders q-ma-md"
          >
            <div class="row items-center">
              <q-icon name="info" class="q-mr-sm" />
              <div>No games found. Adjust filters.</div>
            </div>
          </q-banner>

          <!-- Cards -->
          <q-card
            v-for="game in displayedGames"
            :key="game.id"
            @click="setGameInformation(game)"
            flat
            bordered
            clickable
            square
            v-ripple="{ color: 'secondary' }"
            class="game-card modern rounded-borders cursor-pointer relative-position"
            :class="{ selected: game.id === gameSelection.game.id }"
            role="button"
            tabindex="0"
            @keyup.enter.space="setGameInformation(game)"
            :aria-pressed="game.id === gameSelection.game.id"
            :aria-label="`Select ${game.name}`"
          >
            <!-- Floating platform badge -->
            <q-badge
              class="platform-badge"
              :color="getPlatformColor(getPlatformName(game.platform)).color"
              :text-color="
                getPlatformColor(getPlatformName(game.platform)).text
              "
            >
              {{ getPlatformName(game.platform).split('.')[0] }}
            </q-badge>

            <q-card-section class="q-pa-md column items-start">
              <div class="row items-center justify-between full-width q-mb-sm">
                <q-icon name="sports_esports" size="18px" class="text-grey-7" />
              </div>

              <div class="game-name text-body2 text-weight-medium ellipsis">
                {{
                  game.name.length > 18
                    ? game.name.slice(0, 17) + '…'
                    : game.name
                }}
                <q-tooltip anchor="top middle" self="bottom middle">
                  {{ game.name }}
                </q-tooltip>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </q-card>
    </div>

    <!-- RIGHT: DETAILS -->
    <div class="col-12 col-md-6">
      <q-card
        flat
        bordered
        class="q-pa-md q-my-md rounded-borders details-card shadow-2"
      >
        <q-inner-loading :showing="isLoading">
          <q-spinner-orbit size="96px" color="secondary" />
        </q-inner-loading>

        <template v-if="!isLoading && !gameInformation.game">
          <q-banner class="bg-grey-2 text-grey-8 rounded-borders q-pa-md">
            <div class="row items-center">
              <q-icon name="info" class="q-mr-sm" />
              <div>Please select a game on the left to see details.</div>
            </div>
          </q-banner>
        </template>

        <template v-else-if="gameInformation.game">
          <!-- Header -->
          <div class="row items-center justify-between q-mb-sm">
            <div class="text-h6 text-weight-bold">
              {{ gameInformation.game.name }}
            </div>
            <q-chip
              dense
              square
              outline
              :color="
                getPlatformColor(getPlatformName(gameInformation.game.platform))
                  .color
              "
              :text-color="
                getPlatformColor(getPlatformName(gameInformation.game.platform))
                  .text
              "
            >
              {{ getPlatformName(gameInformation.game.platform).split('.')[0] }}
            </q-chip>
          </div>

          <q-separator spaced />

          <!-- No settings -->
          <div
            v-if="!gameInformation.options.length"
            class="text-italic text-grey"
          >
            This game has no additional settings.
          </div>

          <!-- Settings -->
          <template v-else>
            <div class="section-title q-mb-sm">Settings</div>

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
                  class="col-12 col-sm-6"
                >
                  <KennerSelect
                    :options="findChoicesByOption(option.id)"
                    :label="option.name"
                    option-label="name"
                    dense
                    outlined
                    v-model="
                      gameSelection.selectedOptions.find(
                        (o) => o.id == option.id
                      ).choice
                    "
                    :rules="[(val) => !!val || `${option.name} is required`]"
                    class="full-width"
                  />
                </div>
              </div>
            </div>

            <!-- Toggles -->
            <div v-if="gameInformation.options.some((o) => !o.has_choices)">
              <div class="section-subtitle q-mb-xs">Toggles</div>
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
          </template>
        </template>
      </q-card>
      <KennerButton class="float-right" :disable="!isValid" @click="onSubmit()">
        Save
      </KennerButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch, computed, ref } from 'vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import { useGameSelection } from 'src/composables/gameSelection';
import KennerButton from 'components/base/KennerButton.vue';

const props = defineProps<{
  leagueId: number;
  profileId: number;
  manageOnly?: boolean;
}>();

const {
  gameInformation,
  gameSelection,
  isLoading,
  setGameInformation,
  findChoicesByOption,
  findSelectedOption,
  filter,
  platforms,
  filteredGames,
  loadPlatformsAndGames,
  submitGame,
  isValid,
} = useGameSelection(props.leagueId, props.profileId);

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
const emit = defineEmits(['selection-updated', 'set-submitter', 'on-success']);
watch(gameSelection, (newVal) => {
  emit('selection-updated', newVal);
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

async function onSubmit() {
  try {
    await submitGame(props.manageOnly);
    emit('on-success');
  } catch (e) {
    console.error(e);
  }
}

onMounted(() => {
  loadPlatformsAndGames();
  emit('set-submitter', onSubmit);
});
</script>

<style scoped lang="scss">
/* CSS kept only where Quasar utilities aren't expressive enough */

/* CSS Grid for responsive, evenly-spaced game cards */
.game-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
  max-height: 260px;
  overflow-y: auto;
  padding: 8px 12px 12px;
}

/* Card look & feel for games (hover + selected) */
.game-card {
  background: #f7f7f9;
  transition: box-shadow 0.12s ease, transform 0.12s ease,
    border-color 0.12s ease;
}
.game-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
}
.game-card.selected {
  border: 2px solid var(--q-color-secondary);
  background: #fff;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
}
.game-name {
  font-weight: 600;
}

/* Details card: subtle accent divider */
.details-card {
  position: relative;
  background: white;
  border-left: 4px solid var(--q-color-secondary);
}

/* Section headings */
.section-title {
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--q-dark);
  opacity: 0.85;
}
.section-subtitle {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--q-dark);
  opacity: 0.65;
}
</style>

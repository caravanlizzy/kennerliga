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
          <GameFilter v-model="filter" />

          <!-- Platform multi-select chips -->
          <PlatformMultiSelect
            :isPlatformSelected="isPlatformSelected"
            :togglePlatform="togglePlatform"
          />
        </div>
      </q-card>

      <!-- GAME GRID CARD -->
      <q-card flat bordered class="q-pa-sm q-mt-md rounded-borders">
        <div class="row items-center q-gutter-sm q-px-sm q-pt-sm q-pb-xs">
          <q-icon name="grid_view" size="16px" class="text-grey-7" />
          <div class="text-caption text-uppercase text-grey-7">
            Games ({{ availableGames.length }})
          </div>
        </div>

        <div class="game-grid">
          <!-- Empty state -->
          <NoGamesFound v-if="availableGames.length === 0" />

          <!-- Cards -->
          <GameSelectionCard
            v-for="game in availableGames"
            :key="game.id"
            :game="game"
            :initGameInformation="initGameInformation"
            :gameSelection="gameSelection"
          />
        </div>
      </q-card>
    </div>

    <!-- RIGHT: SELECTED GAME DETAILS -->
    <div class="col-12 col-md-6">
      <GameSelectionForm
        :isLoading="isLoading"
        :isValid="isValid"
        :gameSelection="gameSelection"
        :gameInformation="gameInformation"
        :onSubmit="onSubmit"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, provide, watch } from 'vue';
import { useGameSelection } from 'src/composables/gameSelection';
import GameFilter from 'components/game/selectedGame/GameFilter.vue';
import PlatformMultiSelect from 'components/game/selectedGame/PlatformMultiSelect.vue';
import NoGamesFound from 'components/game/selectedGame/NoGamesFound.vue';
import GameSelectionCard from 'components/game/selectedGame/GameSelectionCard.vue';
import GameSelectionForm from 'components/game/selectedGame/GameSelectionForm.vue';

const props = defineProps<{
  leagueId: number;
  profileId: number;
  manageOnly?: boolean;
}>();

// ---- actions / header wiring ----
const emit = defineEmits<{
  (e: 'selection-updated', value: typeof gameSelection): void;
  (e: 'set-submitter', submitter: () => Promise<void>): void;
  (e: 'on-success'): void;
}>();

const {
  gameInformation,
  gameSelection,
  isLoading,
  filter,
  platforms,
  isValid,
  availableGames,
  initGameInformation,
  togglePlatform,
  isPlatformSelected,
  loadPlatformsAndGames,
  submitGame,
} = useGameSelection(props.leagueId, props.profileId);

provide('platforms', platforms);

// init: load games/platforms and, in edit mode, pre-fill selection
onMounted(async () => {
  await loadPlatformsAndGames();
  emit('set-submitter', onSubmit);
});

watch(gameSelection, (newVal) => {
  emit('selection-updated', newVal);
});

async function onSubmit() {
  try {
    await submitGame(props.manageOnly);
    emit('on-success');
  } catch (e) {
    console.error(e);
  }
}
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

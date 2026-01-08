<template>
  <div class="row q-col-gutter-lg">
    <!-- LEFT: SELECTED GAME DETAILS -->
    <div v-if="gameSelection.game.id > 0" class="col-12 col-md-6 order-md-last">
      <GameSelectionForm
        :game-information="gameInformation"
        :game-selection="gameSelection"
        :is-loading="isLoading"
        :is-valid="isValid"
        :on-submit="onSubmit"
        :visible-options="visibleOptions"
      />
    </div>

    <div class="selector col-12" :class="{ 'col-md-6': gameSelection.game.id > 0 }">
      <!-- FILTER CARD -->
      <q-card flat class="q-pa-md modern-filter-card q-mb-md">
        <div class="row items-center q-gutter-x-sm q-mb-md">
          <q-icon name="tune" size="20px" color="primary" />
          <div class="text-subtitle2 text-weight-bold text-uppercase letter-spacing-1 text-grey-8">Find Your Game</div>
        </div>

        <div class="row q-col-gutter-sm items-center">
          <!-- Search -->
          <div class="col-12 col-sm-6">
            <GameFilter v-model="filter" />
          </div>

          <!-- Platform multi-select chips -->
          <div class="col-12 col-sm-6">
            <PlatformMultiSelect
              :isPlatformSelected="isPlatformSelected"
              :togglePlatform="togglePlatform"
            />
          </div>
        </div>
      </q-card>

      <!-- GAME GRID CARD -->
      <q-card flat class="q-pa-none modern-grid-card">
        <div class="row items-center justify-between q-px-md q-pt-md q-pb-sm">
          <div class="row items-center q-gutter-x-sm">
            <q-icon name="grid_view" size="18px" color="primary" />
            <div class="text-caption text-weight-bold text-uppercase letter-spacing-1 text-grey-7">
              Available Games ({{ availableGames.length }})
            </div>
          </div>
        </div>

        <div class="game-grid custom-scrollbar">
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
  onSuccess?: () => void;
  onError?: () => void;
}>();

// ---- actions / header wiring ----
const emit = defineEmits<{
  (e: 'selection-updated', value: any): void;
  (e: 'selection-valid', value: boolean): void;
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
  visibleOptions,
  initGameInformation,
  togglePlatform,
  isPlatformSelected,
  loadPlatformsAndGames,
  submitGame,
} = useGameSelection(props.leagueId, props.profileId, props.manageOnly);

provide('platforms', platforms);

// init: load games/platforms and, in edit mode, pre-fill selection
onMounted(async () => {
  await loadPlatformsAndGames();
  emit('set-submitter', onSubmit);
});

watch(gameSelection, (newVal) => {
  emit('selection-updated', newVal);
  emit('selection-valid', isValid.value);
});

async function onSubmit() {
  try {
    await submitGame(props.manageOnly);
    emit('on-success');
    await props.onSuccess?.();
  } catch (e) {
    console.error(e);
    props.onError?.();
  }
}
</script>

<style scoped lang="scss">
/* CSS Grid for responsive, evenly-spaced game cards */
.game-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 12px;
  max-height: 380px;
  overflow-y: auto;
  padding: 8px 16px 16px;
}

.modern-filter-card {
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(54, 64, 88, 0.08);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.modern-grid-card {
  border-radius: 16px;
  background: white;
  border: 1px solid rgba(54, 64, 88, 0.08);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
  overflow: hidden;
}

.letter-spacing-1 {
  letter-spacing: 0.05em;
}

.custom-scrollbar {
  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  &::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.1);
    border-radius: 10px;
  }
  &::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 0, 0, 0.2);
  }
}

/* Details card: subtle accent divider handled in GameSelectionForm */
</style>

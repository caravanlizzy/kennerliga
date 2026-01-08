<template>
  <div class="game-selection-container">
    <div class="row q-col-gutter-lg">
      <!-- LEFT SIDE: Filter & Grid -->
      <div class="col-12" :class="{ 'col-md-7': gameSelection.game.id > 0 }">
        <!-- 1. FIND & FILTER & AVAILABLE GAMES SECTION -->
        <div class="selection-browser-card">
          <!-- Find & Filter -->
          <div class="section-container filter-section q-pa-sm q-px-md">
            <div class="row items-center q-gutter-x-sm q-mb-sm">
              <div class="section-icon-box small">
                <q-icon name="search" size="16px" color="primary" />
              </div>
              <div class="text-caption text-weight-bold text-primary text-uppercase letter-spacing-1">Find & Filter</div>
            </div>

            <div class="row q-col-gutter-sm items-center">
              <div class="col-12 col-sm-4">
                <GameFilter v-model="filter" />
              </div>
              <div class="col-12 col-sm-8">
                <PlatformMultiSelect
                  :isPlatformSelected="isPlatformSelected"
                  :togglePlatform="togglePlatform"
                />
              </div>
            </div>
          </div>

          <q-separator />

          <!-- Available Games -->
          <div class="section-container grid-section q-pa-md">
            <div class="row items-center justify-between q-mb-sm">
              <div class="row items-center q-gutter-x-sm">
                <div class="section-icon-box small">
                  <q-icon name="grid_view" size="16px" color="primary" />
                </div>
                <div class="text-caption text-weight-bold text-primary text-uppercase letter-spacing-1">
                  Available Games
                  <q-badge color="primary" outline class="q-ml-xs" style="font-size: 10px; padding: 2px 4px;">{{ availableGames.length }}</q-badge>
                </div>
              </div>
            </div>

            <div class="game-grid custom-scrollbar">
              <NoGamesFound v-if="availableGames.length === 0" />
              <GameSelectionCard
                v-for="game in availableGames"
                :key="game.id"
                :game="game"
                :initGameInformation="initGameInformation"
                :gameSelection="gameSelection"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT SIDE: SELECTION FORM -->
      <div v-if="gameSelection.game.id > 0" class="col-12 col-md-5">
        <div class="section-container form-section sticky-form">
          <div class="row items-center q-gutter-x-sm q-mb-md">
            <div class="section-icon-box accent">
              <q-icon name="check_circle" size="20px" color="white" />
            </div>
            <div class="text-subtitle1 text-weight-bold text-primary">Complete Selection</div>
          </div>

          <GameSelectionForm
            :game-information="gameInformation"
            :game-selection="gameSelection"
            :is-loading="isLoading"
            :is-valid="isValid"
            :on-submit="onSubmit"
            :visible-options="visibleOptions"
          />
        </div>
      </div>
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
.game-selection-container {
  padding: 8px 0;
}

.selection-browser-card {
  border-radius: 16px;
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}


.grid-section {
  background: #f1f3f5;
}

.section-icon-box {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(var(--q-primary), 0.1);
  display: flex;
  align-items: center;
  justify-content: center;

  &.small {
    width: 28px;
    height: 28px;
    border-radius: 8px;
  }

  &.accent {
    background: var(--q-primary);
  }
}

.letter-spacing-1 {
  letter-spacing: 0.05em;
}


.sticky-form {
  @media (min-width: 1024px) {
    position: sticky;
    top: 24px;
  }
}

.game-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 12px;
  max-height: 500px;
  overflow-y: auto;
  padding: 12px;
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
</style>

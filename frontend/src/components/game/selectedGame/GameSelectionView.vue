<template>
  <div class="game-selection-container">
    <div class="row" :class="isMobile ? 'q-col-gutter-y-md' : 'q-col-gutter-lg'">
      <!-- LEFT SIDE: Filter & Grid -->
      <div class="col-12 col-md-7">
        <!-- 1. FIND & FILTER & AVAILABLE GAMES SECTION -->
        <div class="selection-browser-card" :class="{ 'no-shadow no-border': isMobile }">
          <!-- Find & Filter -->
          <div class="section-container filter-section q-pa-sm q-px-md">
            <div
              class="row items-center justify-between no-wrap"
              :class="{ 'cursor-pointer': isMobile }"
              @click="isMobile && (showFilters = !showFilters)"
            >
              <div class="row items-center q-gutter-x-sm" :class="{ 'q-mb-sm': !isMobile }">
                <div class="section-icon-box small">
                  <q-icon :name="isMobile ? 'filter_list' : 'search'" size="16px" color="primary" />
                </div>
                <div class="text-caption text-weight-bold text-primary text-uppercase letter-spacing-1 relative-position">
                  {{ isMobile ? 'Filter' : 'Find & Filter' }}
                  <q-badge
                    v-if="isMobile && hasActiveFilters"
                    color="primary"
                    rounded
                    class="q-ml-xs"
                    style="width: 8px; height: 8px; min-height: 8px; padding: 0;"
                  />
                </div>
              </div>
              <q-icon
                v-if="isMobile"
                :name="showFilters ? 'expand_less' : 'expand_more'"
                color="grey-6"
                size="20px"
              />
            </div>

            <q-slide-transition>
              <div v-show="!isMobile || showFilters">
                <div class="row q-col-gutter-sm items-center q-pt-xs">
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
            </q-slide-transition>
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
                  {{ isMobile ? 'Games' : 'Available Games' }}
                  <q-badge color="primary" outline class="q-ml-xs" style="font-size: 10px; padding: 2px 4px;">{{ availableGames.length }}</q-badge>
                </div>
              </div>

              <q-btn
                dense
                unelevated
                no-caps
                color="primary"
                :icon="isRandomizing ? 'casino' : 'shuffle'"
                :label="isMobile ? '' : (isRandomizing ? 'Rolling…' : 'Pick a random game for me')"
                :disable="isRandomizing || randomizableGames.length === 0"
                class="random-btn"
                :class="{ 'random-btn--rolling': isRandomizing, 'q-px-sm': isMobile }"
                @click="randomizeGame"
              >
                <q-tooltip v-if="memberCount">
                  Chooses a random game that fits {{ memberCount }} player{{ memberCount === 1 ? '' : 's' }}.
                </q-tooltip>
                <q-tooltip v-else>
                  Chooses a random game from the currently available list.
                </q-tooltip>
              </q-btn>
            </div>

            <div class="game-grid custom-scrollbar" ref="gridRef">
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
      <div class="col-12 col-md-5">
        <div v-if="gameSelection.game.id > 0" class="form-section sticky-form">
          <GameSelectionForm
            :game-information="gameInformation"
            :game-selection="gameSelection"
            :is-loading="isLoading"
            :is-valid="isValid"
            :on-submit="onSubmit"
            :visible-options="visibleOptions"
          >
            <template #header>
              <div class="row items-center q-gutter-x-sm">
                <div
                  class="section-icon-box"
                  :class="isValid ? 'selected-bg' : 'incomplete-bg'"
                >
                  <q-icon :name="isValid ? 'check_circle' : 'edit_note'" size="20px" :color="isValid ? 'white' : 'grey-7'" />
                </div>
                <div
                  class="text-subtitle1 text-weight-bold transition-all ellipsis"
                  :class="isValid ? 'text-selected' : 'text-grey-7'"
                >
                  {{ isValid ? 'Ready to Confirm' : 'Complete Selection' }}
                </div>
              </div>
            </template>
          </GameSelectionForm>
        </div>

        <!-- Placeholder when no game is selected -->
        <div v-else-if="!isMobile" class="placeholder-section flex flex-center">
          <div class="text-center q-pa-xl">
            <div class="placeholder-icon-container q-mb-lg">
              <q-icon name="ads_click" size="64px" color="grey-3" />
            </div>
            <div class="text-h6 text-grey-4 text-weight-bold tracking-tight">Select a Game</div>
            <div class="text-caption text-grey-5 q-mt-sm">
              Pick a game from the list<br>to configure your selection
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, provide, ref, watch } from 'vue';
import { useGameSelection } from 'src/composables/gameSelection';
import { useResponsive } from 'src/composables/responsive';
import GameFilter from 'components/game/selectedGame/GameFilter.vue';
import PlatformMultiSelect from 'components/game/selectedGame/PlatformMultiSelect.vue';
import NoGamesFound from 'components/game/selectedGame/NoGamesFound.vue';
import GameSelectionCard from 'components/game/selectedGame/GameSelectionCard.vue';
import GameSelectionForm from 'components/game/selectedGame/GameSelectionForm.vue';
import type { TGameDto } from 'src/types';

const props = defineProps<{
  leagueId: number;
  profileId: number;
  manageOnly?: boolean;
  memberCount?: number;
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

const { isMobile } = useResponsive();
const showFilters = ref(false);
const gridRef = ref<HTMLElement | null>(null);

const hasActiveFilters = computed(() => {
  return (filter.value && filter.value.length > 0) ||
    (platforms.value && platforms.value.some(p => isPlatformSelected(p.id)));
});

provide('platforms', platforms);

// init: load games/platforms and, in edit mode, pre-fill selection
onMounted(async () => {
  await loadPlatformsAndGames();
  emit('set-submitter', onSubmit);
});

watch(() => gameSelection.game.id, (newId) => {
  if (newId > 0) {
    // 1. Scroll the card into view (especially useful for the scrollable grid on desktop)
    setTimeout(() => {
      const cardElement = gridRef.value?.querySelector('.game-card.selected');
      if (cardElement) {
        cardElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }, 50);

    // 2. Scroll to form on mobile
    if (isMobile.value) {
      setTimeout(() => {
        const formElement = document.querySelector('.sticky-form');
        if (formElement) {
          formElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 150);
    }
  }
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

// ---- randomize game ----
const isRandomizing = ref(false);

// Games that match current league member count (falls back to all available
// games when member count is unknown or game min/max are missing).
const randomizableGames = computed<TGameDto[]>(() => {
  const games = availableGames.value ?? [];
  const count = props.memberCount ?? 0;
  if (!count) return games;
  const matching = games.filter((g) => {
    const min = typeof g.min_players === 'number' ? g.min_players : undefined;
    const max = typeof g.max_players === 'number' ? g.max_players : undefined;
    if (min === undefined && max === undefined) return true;
    if (min !== undefined && count < min) return false;
    if (max !== undefined && count > max) return false;
    return true;
  });
  return matching.length > 0 ? matching : games;
});

function pickRandom<T>(items: T[]): T | undefined {
  if (items.length === 0) return undefined;
  return items[Math.floor(Math.random() * items.length)];
}

async function randomizeGame() {
  const pool = randomizableGames.value;
  if (pool.length === 0 || isRandomizing.value) return;

  isRandomizing.value = true;
  try {
    const finalPick = pickRandom(pool)!;
    await initGameInformation(finalPick);
  } finally {
    isRandomizing.value = false;
  }
}
</script>

<style scoped lang="scss">
.game-selection-container {
  padding: 8px 0;
  // min-width removed - now handled by ManagerFormsDialog
}

.selection-browser-card {
  border-radius: 24px;
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
  overflow: hidden;

  &.no-shadow {
    box-shadow: none;
  }
  &.no-border {
    border: none;
  }
}

.filter-section {
  background: linear-gradient(to bottom, #ffffff, #fcfcfc);
}

.grid-section {
  background: #f8fafc;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.section-icon-box {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;

  &.small {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    box-shadow: none;
  }

  &.selected-bg {
    background: linear-gradient(135deg, $kenner-red 0%, darken($kenner-red, 10%) 100%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 4px 12px rgba($kenner-red, 0.15);
  }

  &.incomplete-bg {
    background: #f8fafc;
    border: 1px solid rgba(0, 0, 0, 0.05);
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.02);
  }
}

.transition-all {
  transition: all 0.3s ease;
}

.text-selected {
  color: $kenner-red;
}

.letter-spacing-1 {
  letter-spacing: 0.05em;
}


.sticky-form {
  @media (min-width: 1024px) {
    position: sticky;
    top: 24px;
    height: fit-content;
  }
}

.placeholder-section {
  border: 2px dashed rgba(0, 0, 0, 0.05);
  border-radius: 24px;
  height: 100%;
  min-height: 400px;
  background: rgba(0, 0, 0, 0.01);
}

.placeholder-icon-container {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: white;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(0, 0, 0, 0.02);
}

.game-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 12px;
  max-height: 520px;
  overflow-y: auto;
  padding: 16px;
  box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.03);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.5);

  @media (max-width: 600px) {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 8px;
    padding: 8px;
    max-height: none;
  }
}

.random-btn {
  border-radius: 999px;
  font-weight: 700;
  letter-spacing: 0.02em;
  padding: 4px 12px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover:not(:disabled) {
    // transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(var(--q-primary), 0.25);
  }

  :deep(.q-icon) {
    transition: transform 0.3s ease;
  }

  &--rolling {
    :deep(.q-icon) {
      animation: dice-roll 0.6s linear infinite;
    }
  }
}

@keyframes dice-roll {
  0%   { transform: rotate(0deg)   scale(1);   }
  50%  { transform: rotate(180deg) scale(1.15); }
  100% { transform: rotate(360deg) scale(1);   }
}

.game-grid :deep(.game-card.selected) {
  animation: pick-pop 0.35s ease;
  border-color: $kenner-red !important;
}

@keyframes pick-pop {
  0%   { transform: scale(1);    }
  60%  { transform: scale(1.06); }
  100% { transform: scale(1);    }
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

<template>
  <q-card
    @click="initGameInformation(game)"
    flat
    clickable
    v-ripple="{ color: 'primary' }"
    class="game-card modern-card cursor-pointer relative-position"
    :class="{
      selected: game.id === gameSelection.game.id
    }"
    role="button"
    tabindex="0"
    @keyup.enter.space="initGameInformation(game)"
  >
    <!-- Floating platform badge -->
    <q-badge
      class="platform-badge absolute-top-right q-ma-xs shadow-1"
      :color="getPlatformColor(getPlatformName(platforms, game.platform)).color"
      :text-color="getPlatformColor(getPlatformName(platforms, game.platform)).text"
      style="z-index: 1; border-radius: 4px; font-size: 9px; padding: 1px 4px;"
    >
      {{ getPlatformName(platforms, game.platform).split('.')[0] }}
    </q-badge>

    <q-card-section class="q-pa-xs column items-center justify-center text-center full-height">
      <div class="icon-container q-mb-xs">
        <div class="icon-circle" :class="{
          'bg-selected-soft': game.id === gameSelection.game.id
        }">
          <q-icon
            name="sports_esports"
            size="20px"
            :class="(game.id === gameSelection.game.id) ? 'text-selected' : 'text-grey-6'"
            class="transition-all"
          />
        </div>
      </div>

      <div class="game-name text-weight-bold ellipsis-2-lines text-dark">
        {{ game.name }}
        <q-tooltip anchor="top middle" self="bottom middle" :offset="[0, 8]">
          {{ game.name }}
        </q-tooltip>
      </div>
    </q-card-section>
  </q-card>
</template>

<style lang="scss" scoped>
.modern-card {
  border-radius: 16px;
  background: white;
  border: 2px solid transparent;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.08);
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  height: 100px;
  overflow: hidden;

  @media (max-width: 600px) {
    height: 80px;
    border-radius: 12px;
  }

  &.selected {
    border: 2px solid $kenner-red;
    box-shadow:
      0 12px 28px rgba($kenner-red, 0.2),
      inset 0 0 20px rgba($kenner-red, 0.1);
    background:
      radial-gradient(circle at center, rgba($kenner-red, 0.06) 0%, transparent 70%),
      repeating-conic-gradient(from 0deg, transparent 0deg 20deg, rgba($kenner-red, 0.02) 20deg 40deg),
      white;

    .icon-circle {
      background: rgba($kenner-red, 0.15);
    }
  }
}

.text-selected {
  color: $kenner-red !important;
}

.bg-selected-soft {
  background: rgba($kenner-red, 0.15) !important;
}

.game-name {
  font-size: 0.85rem;
  font-weight: 700 !important;
  line-height: 1.2;
  letter-spacing: -0.01em;
  width: 100%;
  color: #2d3748;

  @media (max-width: 600px) {
    font-size: 0.7rem;
  }
}

.transition-all {
  transition: all 0.3s ease;
}

.icon-circle {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e9ecef;
  transition: all 0.3s ease;

  @media (max-width: 600px) {
    width: 24px;
    height: 24px;
    border-radius: 8px;
    
    .q-icon {
      font-size: 16px !important;
    }
  }
}

</style>
<script setup lang="ts">
import { getPlatformColor, getPlatformName } from 'src/composables/gameSelection';
import { TPlatform, TGameDto, TGameSelection } from 'src/types';
import { inject } from 'vue';

const platforms = inject<TPlatform[]>('platforms', []);

defineProps<{
  game: TGameDto;
  initGameInformation: (game: TGameDto) => void;
  gameSelection: TGameSelection;
}>();
</script>

<template>
  <q-card
    @click="initGameInformation(game)"
    flat
    bordered
    clickable
    v-ripple="{ color: 'primary' }"
    class="game-card modern-card cursor-pointer relative-position"
    :class="{ selected: game.id === gameSelection.game.id }"
    role="button"
    tabindex="0"
    @keyup.enter.space="initGameInformation(game)"
  >
    <!-- Floating platform badge -->
    <q-badge
      class="platform-badge absolute-top-right q-ma-xs shadow-1"
      :color="getPlatformColor(getPlatformName(platforms, game.platform)).color"
      :text-color="getPlatformColor(getPlatformName(platforms, game.platform)).text"
      style="z-index: 1; border-radius: 4px;"
    >
      {{ getPlatformName(platforms, game.platform).split('.')[0] }}
    </q-badge>

    <q-card-section class="q-pa-md column items-center justify-center text-center full-height">
      <div class="icon-container q-mb-sm">
        <div class="icon-circle" :class="{ 'bg-primary-soft': game.id === gameSelection.game.id }">
          <q-icon
            name="sports_esports"
            size="28px"
            :class="game.id === gameSelection.game.id ? 'text-primary' : 'text-grey-5'"
            class="transition-all"
          />
        </div>
      </div>

      <div class="game-name text-caption text-weight-bold ellipsis-2-lines line-height-1 text-dark">
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
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(54, 64, 88, 0.08);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  height: 100px;
  overflow: hidden;

  &:hover {
    background: white;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
    border-color: rgba(54, 64, 88, 0.2);

    .icon-circle {
      background: rgba(var(--q-primary), 0.08);
      transform: scale(1.05);
    }
    .icon-container .q-icon {
      color: var(--q-primary) !important;
    }
  }

  &.selected {
    background: white;
    border: 2px solid var(--q-primary);
    box-shadow: 0 12px 32px rgba(var(--q-primary), 0.15);
    transform: scale(1.02);

    .icon-circle {
      background: rgba(var(--q-primary), 0.12);
    }

    &::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: var(--q-primary);
    }
  }
}

.line-height-1 {
  line-height: 1.2;
}

.transition-all {
  transition: all 0.3s ease;
}

.icon-circle {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.03);
  transition: all 0.3s ease;
}

.bg-primary-soft {
  background: rgba(var(--q-primary), 0.1) !important;
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

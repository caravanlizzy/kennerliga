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
      style="z-index: 1; border-radius: 4px; font-size: 9px; padding: 1px 4px;"
    >
      {{ getPlatformName(platforms, game.platform).split('.')[0] }}
    </q-badge>

    <q-card-section class="q-pa-xs column items-center justify-center text-center full-height">
      <div class="icon-container q-mb-xs">
        <div class="icon-circle" :class="{ 'bg-primary-soft': game.id === gameSelection.game.id }">
          <q-icon
            name="sports_esports"
            size="20px"
            :class="game.id === gameSelection.game.id ? 'text-primary' : 'text-grey-6'"
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
  border: 1px solid rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  height: 100px;
  overflow: hidden;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    border-color: var(--q-primary);
    transform: translateY(-2px);

    .icon-circle {
      background: rgba(var(--q-primary), 0.08);
    }
    .icon-container .q-icon {
      color: var(--q-primary) !important;
    }
  }

  &.selected {
    border: 2px solid var(--q-primary);
    box-shadow: 0 8px 20px rgba(var(--q-primary), 0.1);

    .icon-circle {
      background: rgba(var(--q-primary), 0.12);
    }
  }
}

.game-name {
  font-size: 0.8rem;
  font-weight: 600 !important;
  line-height: 1.15;
  width: 100%;
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

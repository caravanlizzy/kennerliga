<template>
  <q-card
    @click="initGameInformation(game)"
    flat
    bordered
    clickable
    square
    v-ripple="{ color: 'secondary' }"
    class="game-card modern rounded-borders cursor-pointer relative-position"
    :class="{ selected: game.id === gameSelection.game.id }"
    role="button"
    tabindex="0"
    @keyup.enter.space="initGameInformation(game)"
  >
    <!-- Floating platform badge -->
    <q-badge
      class="platform-badge"
      :color="getPlatformColor(getPlatformName(platforms, game.platform)).color"
      :text-color="getPlatformColor(getPlatformName(platforms, game.platform)).text"
    >
      {{ getPlatformName(platforms, game.platform).split('.')[0] }}
    </q-badge>

    <q-card-section class="q-pa-md column items-start">
      <div class="row items-center justify-between full-width q-mb-sm">
        <q-icon name="sports_esports" size="18px" class="text-grey-7" />
      </div>

      <div class="game-name text-body2 text-weight-medium ellipsis">
        {{ game.name.length > 18 ? game.name.slice(0, 17) + '…' : game.name }}
        <q-tooltip anchor="top middle" self="bottom middle">
          {{ game.name }}
        </q-tooltip>
      </div>
    </q-card-section>
  </q-card>
</template>
<script setup lang="ts">
import { getPlatformColor, getPlatformName } from 'src/composables/gameSelection';
import { TPlatform } from 'src/models/gameModels';
import { inject } from 'vue';

const platforms = inject<TPlatform[]>('platforms', []);

defineProps<{
  game: any;
  initGameInformation: (game: any) => void;
  gameSelection: any;
}>();
</script>

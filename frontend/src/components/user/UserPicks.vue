<template>
  <q-card flat bordered class="q-mb-lg surface-card">
    <q-card-section class="surface-card-header text-weight-bold text-uppercase letter-spacing-1 row items-center justify-between q-py-sm">
      <div class="row items-center q-gutter-x-sm">
        <q-icon name="push_pin" size="xs" />
        <div class="text-caption text-weight-bolder">Game Picks</div>
        <q-select
          :model-value="selectedYear"
          :options="availableYears"
          dense
          borderless
          emit-value
          map-options
          style="min-width: 80px"
          class="text-weight-bolder text-primary"
          @update:model-value="$emit('update:selectedYear', $event)"
        />
      </div>
      <q-icon name="help_outline" size="xs" class="cursor-pointer opacity-50">
        <q-tooltip class="bg-dark text-white shadow-4" anchor="top middle" self="bottom middle" :offset="[10, 10]">
          Maximum <strong>{{ maxGameLimit }}</strong> picks per game per year
        </q-tooltip>
      </q-icon>
    </q-card-section>
    <q-list separator class="q-pb-xs">
      <q-item v-for="game in pickedGames" :key="game.name + game.platform" class="q-py-md transition-all pick-item">
        <q-item-section avatar min-width="40px" class="q-pr-none">
          <q-avatar size="36px" color="primary" text-color="white" icon="sports_esports" class="shadow-1" />
        </q-item-section>
        <q-item-section>
          <q-item-label class="text-weight-bolder text-heading ellipsis">{{ game.name }}</q-item-label>
          <q-item-label caption class="text-uppercase text-grey-6 text-weight-bold" style="font-size: 0.6rem; letter-spacing: 0.5px;">{{ game.platform }}</q-item-label>
        </q-item-section>
        <q-item-section side>
          <q-badge
            :color="game.limit_exceeded ? 'negative' : 'primary'"
            :outline="!game.limit_exceeded"
            class="text-weight-bolder q-px-sm"
            style="border-radius: 6px; padding: 4px 8px;"
          >
            {{ game.count }} / {{ maxGameLimit }}
          </q-badge>
        </q-item-section>
      </q-item>
      <q-item v-if="pickedGames.length === 0">
        <q-item-section class="text-grey-5 text-italic text-center q-pa-lg">
          <q-icon name="history" size="md" class="q-mb-sm opacity-20" />
          <div class="text-caption">No picks recorded for {{ selectedYear }}</div>
        </q-item-section>
      </q-item>
    </q-list>
  </q-card>
</template>

<script setup lang="ts">
defineProps<{
  pickedGames: any[];
  maxGameLimit: number;
  selectedYear: number;
  availableYears: number[];
}>();

defineEmits<{
  (e: 'update:selectedYear', value: number): void;
}>();
</script>

<style scoped lang="scss">
.surface-card {
  background: var(--surface-bg) !important;
  border-color: var(--surface-border) !important;
  border-radius: 16px;
  transition: all 0.3s ease;

  &:hover {
    border-color: var(--surface-border-strong) !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  }
}

.pick-item {
  &:hover {
    background: #f8fafc;
  }
}

.surface-card-header {
  background: var(--surface-header-bg);
  color: var(--surface-header-text);
  border-bottom: 1px solid var(--divider);
}

.letter-spacing-1 { letter-spacing: 1px; }
</style>

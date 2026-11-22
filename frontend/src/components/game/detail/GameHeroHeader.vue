<template>
  <q-card flat class="game-hero-card">
    <q-card-section :class="isMobile ? 'q-pa-sm' : 'q-pa-lg'">
      <div
        class="row items-start justify-between"
        :class="isMobile ? 'q-col-gutter-xs' : 'q-col-gutter-md'"
      >
        <div>
          <!-- Badges Row -->
          <div
            class="row items-center q-gutter-x-sm q-gutter-y-xs"
            :class="isMobile ? 'q-mb-xs' : 'q-mb-sm'"
          >
            <q-btn
              flat
              dense
              no-caps
              size="sm"
              color="grey-7"
              icon="arrow_back"
              label="Statistics"
              class="q-mr-xs"
              @click="$emit('back')"
            />
            <q-badge
              color="primary"
              text-color="white"
              class="q-px-sm text-weight-bold"
            >
              {{ game.platform.name || 'Board Game' }}
            </q-badge>
            <q-badge color="secondary" text-color="white" class="q-px-sm">
              {{ game.min_players }} - {{ game.max_players }} Players
            </q-badge>
            <q-badge
              v-if="game.is_asymmetric"
              color="purple-1"
              text-color="purple-9"
              class="q-px-sm text-weight-medium"
            >
              <q-icon name="shield" size="12px" class="q-mr-xs" />
              Asymmetric Factions
            </q-badge>
            <q-badge
              v-if="!(game.selectable ?? true)"
              color="red-1"
              text-color="negative"
              class="q-px-sm text-weight-bold"
            >
              <q-icon name="block" size="12px" class="q-mr-xs" />
              Not Selectable
            </q-badge>
          </div>

          <!-- Title -->
          <h1
            class="text-weight-bolder text-grey-9 q-my-none"
            :class="isMobile ? 'text-h5' : 'text-h4'"
          >
            {{ game.name }}
          </h1>
          <div
            v-if="game.short_name && game.short_name !== game.name"
            class="text-subtitle2 text-grey-6 q-mt-xs"
          >
            ({{ game.short_name }})
          </div>
        </div>

        <!-- Action Buttons for Admins -->
        <div v-if="isAdmin" class="row items-center q-gutter-sm q-mt-xs">
          <KennerButton
            outline
            no-caps
            size="sm"
            color="secondary"
            icon="settings"
            label="View Configuration"
            @click="$emit('viewConfig', game.id)"
          />
          <KennerButton
            outline
            no-caps
            size="sm"
            color="primary"
            icon="edit"
            label="Edit Game"
            @click="$emit('editGame', game.id)"
          />
        </div>
      </div>

      <!-- Filter Toolbar within Game Details -->
      <q-separator :class="isMobile ? 'q-my-sm' : 'q-my-md'" />

      <div
        class="row items-center justify-between"
        :class="isMobile ? 'q-col-gutter-xs' : 'q-col-gutter-sm'"
      >
        <!-- Player Count Chips -->
        <div :class="isMobile ? 'col-auto' : 'col-12 col-sm-auto'">
          <div
            class="filter-box row items-center q-gutter-x-xs q-py-xs"
            :class="isMobile ? 'q-px-xs filter-box--mobile' : 'q-px-sm'"
          >
            <q-icon
              name="groups"
              :size="isMobile ? '16px' : '18px'"
              class="q-mr-xs text-primary"
            />
            <span
              v-if="!isMobile"
              class="text-caption text-weight-bold text-grey-8 q-mr-xs"
            >
              Player Count:
            </span>
            <q-chip
              clickable
              dense
              :outline="!isAllPlayerCountsSelected"
              :color="isAllPlayerCountsSelected ? 'primary' : 'grey-7'"
              text-color="white"
              size="sm"
              class="text-weight-bold"
              style="border-radius: 4px"
              @click="$emit('toggleAllPlayerCounts')"
            >
              All
            </q-chip>
            <q-chip
              v-for="pc in availablePlayerCounts"
              :key="pc"
              clickable
              dense
              :outline="!selectedPlayerCounts.includes(pc)"
              :color="selectedPlayerCounts.includes(pc) ? 'primary' : 'grey-7'"
              text-color="white"
              size="sm"
              class="text-weight-bold"
              style="border-radius: 4px"
              @click="$emit('togglePlayerCount', pc)"
            >
              {{ pc.toUpperCase() }}
            </q-chip>
          </div>
        </div>

        <!-- Years Filter -->
        <div
          :class="isMobile ? 'col years-filter--mobile' : 'col-12 col-sm-auto years-filter'"
          :style="{ minWidth: isMobile ? '110px' : '170px' }"
        >
          <KennerSelect
            :model-value="selectedYears"
            :options="yearOptions"
            label="Years"
            multiple
            clearable
            dense
            :display-value="yearsDisplayValue"
            @update:model-value="(val) => $emit('update:selectedYears', val)"
          />
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import KennerButton from 'components/base/KennerButton.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import type { TGameDto } from 'src/types';
import { useResponsive } from 'src/composables/responsive';

const { isMobile } = useResponsive();

defineProps<{
  game: TGameDto;
  isAdmin: boolean;
  availablePlayerCounts: string[];
  selectedPlayerCounts: string[];
  isAllPlayerCountsSelected: boolean;
  selectedYears: number[];
  yearOptions: any[];
  yearsDisplayValue: string;
}>();

defineEmits<{
  (e: 'back'): void;
  (e: 'viewConfig', gameId: number): void;
  (e: 'editGame', gameId: number): void;
  (e: 'toggleAllPlayerCounts'): void;
  (e: 'togglePlayerCount', pc: string): void;
  (e: 'update:selectedYears', years: number[]): void;
}>();
</script>

<style scoped>
.game-hero-card {
  border-radius: 12px;
  background: linear-gradient(
    135deg,
    rgba(var(--q-primary-rgb, 25, 118, 210), 0.05) 0%,
    rgba(255, 255, 255, 0.9) 100%
  );
  border: 1px solid var(--kenner-border-subtle);
}

.body--dark .game-hero-card {
  background: linear-gradient(
    135deg,
    rgba(var(--q-primary-rgb, 25, 118, 210), 0.12) 0%,
    rgba(30, 30, 30, 0.9) 100%
  );
}

.filter-box {
  background: rgba(0, 0, 0, 0.03);
  border-radius: 6px;
  border: 1px solid var(--kenner-border-subtle);

  &--mobile {
    min-height: 32px;
    padding: 2px 4px;
  }
}

@media (max-width: 599px) {
  .years-filter--mobile {
    :deep(.q-field__control) {
      min-height: 34px;
      height: 34px;
    }
  }
}
</style>

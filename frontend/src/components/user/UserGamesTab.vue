<template>
  <div class="user-games-tab">
    <!-- Top Games Highlight -->
    <div v-if="topGames.length > 0" class="q-mb-xl">
      <div class="row items-center q-mb-md">
        <q-icon name="stars" color="amber-8" size="24px" class="q-mr-sm" />
        <div class="text-h5 text-weight-bolder text-heading tracking-tighter">Hall of Fame</div>
        <q-space />
        <div class="text-caption text-grey-6 text-uppercase text-weight-bold letter-spacing-1">Best Winrates</div>
      </div>
      <div class="row q-col-gutter-md">
        <div v-for="(game, idx) in topGames" :key="'top-'+game.name" class="col-12 col-sm-4">
          <q-card flat class="top-game-card relative-position transition-all overflow-hidden" :class="`rank-${idx+1}`">
            <div class="rank-badge absolute-top-left q-pa-sm text-weight-bolder shadow-2">
              <q-icon v-if="idx === 0" name="emoji_events" size="14px" class="q-mr-xs" />
              #{{ idx + 1 }}
            </div>
            <q-card-section class="q-pt-xl q-pb-md text-center">
              <div class="text-subtitle1 text-weight-bolder text-heading ellipsis q-mb-xs">{{ game.name }}</div>
              <div class="row justify-center q-gutter-x-md q-mt-sm">
                <div class="column">
                  <div class="text-h5 text-weight-bolder" :class="idx === 0 ? 'text-positive' : 'text-grey-9'">{{ game.winRate.toFixed(0) }}%</div>
                  <div class="text-caption text-grey-6 text-uppercase text-weight-bolder" style="font-size: 0.55rem">Winrate</div>
                </div>
                <q-separator vertical class="q-my-xs opacity-30" style="height: 30px" />
                <div class="column">
                  <div class="text-h5 text-weight-bolder" :class="idx === 0 ? 'text-primary' : 'text-grey-9'">#{{ game.avgPos.toFixed(1) }}</div>
                  <div class="text-caption text-grey-6 text-uppercase text-weight-bolder" style="font-size: 0.55rem">Avg Pos</div>
                </div>
              </div>
              <q-chip dense outline color="grey-4" text-color="grey-7" class="q-mt-md text-weight-bold" style="font-size: 0.65rem">
                {{ game.count }} {{ game.count === 1 ? 'PLAY' : 'TOTAL PLAYS' }}
              </q-chip>
            </q-card-section>
            <div class="card-footer-accent" :class="`bg-rank-${idx+1}`" />
          </q-card>
        </div>
      </div>
    </div>

    <!-- All Games Statistics -->
    <div>
      <div class="row items-center justify-between q-mb-md q-gutter-y-sm">
        <div class="row items-center">
          <q-icon name="grid_view" color="primary" size="24px" class="q-mr-sm" />
          <div class="text-h5 text-weight-bolder text-heading tracking-tighter">Games Library</div>
        </div>
        <div class="search-input-wrapper">
          <q-input
            :model-value="gameSearch"
            outlined
            dense
            rounded
            placeholder="Search your library..."
            bg-color="white"
            class="search-input"
            @update:model-value="$emit('update:gameSearch', $event)"
          >
            <template #prepend>
              <q-icon name="search" size="xs" color="grey-5" />
            </template>
            <template v-if="gameSearch" #append>
              <q-icon name="close" size="xs" class="cursor-pointer" @click="$emit('update:gameSearch', '')" />
            </template>
          </q-input>
        </div>
      </div>

      <div v-if="filteredGameStats.length === 0" class="text-center q-pa-xl surface-card rounded-borders-12 empty-state-container">
        <div class="column items-center">
          <q-icon name="search_off" size="64px" class="q-mb-md text-grey-3" />
          <div class="text-h6 text-weight-bold text-grey-8">No matching games</div>
          <div class="text-caption text-grey-6">Try adjusting your search terms</div>
          <q-btn
            v-if="gameSearch"
            flat
            color="primary"
            label="Clear Search"
            class="q-mt-md"
            @click="$emit('update:gameSearch', '')"
          />
        </div>
      </div>

      <div v-else class="row q-col-gutter-md">
        <div v-for="game in filteredGameStats" :key="game.name" class="col-12 col-sm-6 col-md-4">
          <UserGameCard :game="game" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import UserGameCard from 'components/user/UserGameCard.vue';

defineProps<{
  topGames: any[];
  filteredGameStats: any[];
  gameSearch: string;
}>();

defineEmits<{
  (e: 'update:gameSearch', value: string): void;
}>();
</script>

<style scoped lang="scss">
.tracking-tighter { letter-spacing: -1px; }
.letter-spacing-1 { letter-spacing: 1px; }

.top-game-card {
  border-radius: 20px;
  background: #ffffff;
  border: 1px solid var(--surface-border);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);

  &:hover {
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
  }

  &.rank-1 { border-color: rgba(255, 193, 7, 0.4); background: linear-gradient(135deg, #fffcf0 0%, #ffffff 100%); }
  &.rank-2 { border-color: rgba(176, 190, 197, 0.4); background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%); }
  &.rank-3 { border-color: rgba(255, 152, 0, 0.4); background: linear-gradient(135deg, #fffaf5 0%, #ffffff 100%); }

  .rank-badge {
    border-bottom-right-radius: 14px;
    font-size: 0.8rem;
    padding: 6px 14px;
    z-index: 2;
    font-weight: 900;
  }
  &.rank-1 .rank-badge { background: #ffc107; color: #000; }
  &.rank-2 .rank-badge { background: #b0bec5; color: #fff; }
  &.rank-3 .rank-badge { background: #ff9800; color: #fff; }
}

.bg-rank-1 { background: #ffc107; }
.bg-rank-2 { background: #b0bec5; }
.bg-rank-3 { background: #ff9800; }

.card-footer-accent {
  height: 4px;
  width: 100%;
  position: absolute;
  bottom: 0;
}

.surface-card {
  background: var(--surface-bg) !important;
  border-color: var(--surface-border) !important;
  border-radius: 16px;
}

.empty-state-container {
  border: 2px dashed var(--divider);
  background: transparent !important;
}

.search-input-wrapper {
  min-width: 280px;
  @media (max-width: 599px) {
    width: 100%;
  }
}

.search-input {
  transition: all 0.3s ease;
  :deep(.q-field__control) {
    border-color: var(--surface-border) !important;
    background: #ffffff !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    &.q-field__control--focused {
      box-shadow: 0 4px 12px rgba(25, 118, 210, 0.15); // approximation of primary
    }
  }
}

.text-heading { color: var(--text-heading) !important; }
</style>

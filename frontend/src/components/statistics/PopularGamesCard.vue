<template>
  <q-card flat bordered class="popular-games-card">
    <q-card-section class="q-pb-sm">
      <div class="row items-center no-wrap">
        <div class="stat-icon-box q-mr-sm">
          <q-icon name="leaderboard" color="primary" size="22px" />
        </div>
        <div class="column">
          <div class="text-subtitle1 text-weight-bolder text-dark line-height-1">
            Picks &amp; Bans
          </div>
          <div class="text-caption text-grey-6">
            The games players choose most &mdash; and veto most.
          </div>
        </div>
      </div>
    </q-card-section>

    <q-separator class="q-mx-md" />

    <q-card-section class="row q-col-gutter-md">
      <div class="col-12 col-sm-6">
        <div class="podium-title row items-center q-mb-sm">
          <q-icon name="check_circle" size="16px" class="text-positive q-mr-xs" />
          <span class="text-caption text-weight-bolder text-uppercase text-grey-8">
            Most Picked
          </span>
        </div>
        <div v-if="mostPicked.length === 0" class="text-caption text-grey-6 q-py-sm">
          No picks recorded yet.
        </div>
        <div
          v-for="(game, idx) in mostPicked"
          :key="`pick-${game.game_id}`"
          class="popular-row row items-center no-wrap"
          @click="$emit('select', game.game_id)"
        >
          <span class="rank-badge" :class="`rank-badge--${idx}`">{{ idx + 1 }}</span>
          <span class="popular-row__name ellipsis">{{ game.name }}</span>
          <span class="popular-row__count text-positive">{{ game.count }}&times;</span>
        </div>
      </div>

      <div class="col-12 col-sm-6">
        <div class="podium-title row items-center q-mb-sm">
          <q-icon name="block" size="16px" class="text-negative q-mr-xs" />
          <span class="text-caption text-weight-bolder text-uppercase text-grey-8">
            Most Banned
          </span>
        </div>
        <div v-if="mostBanned.length === 0" class="text-caption text-grey-6 q-py-sm">
          No bans recorded yet.
        </div>
        <div
          v-for="(game, idx) in mostBanned"
          :key="`ban-${game.game_id}`"
          class="popular-row row items-center no-wrap"
          @click="$emit('select', game.game_id)"
        >
          <span class="rank-badge" :class="`rank-badge--${idx}`">{{ idx + 1 }}</span>
          <span class="popular-row__name ellipsis">{{ game.name }}</span>
          <span class="popular-row__count text-negative">{{ game.count }}&times;</span>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { TPopularGames } from 'src/types';

const props = defineProps<{ popular: TPopularGames | null }>();

defineEmits<{ (e: 'select', gameId: number): void }>();

const mostPicked = computed(() => props.popular?.most_picked ?? []);
const mostBanned = computed(() => props.popular?.most_banned ?? []);
</script>

<style scoped lang="scss">
.stat-icon-box {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(99, 102, 241, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.podium-title {
  letter-spacing: 0.04em;
}

.popular-row {
  gap: 8px;
  padding: 6px 4px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.15s ease;

  & + .popular-row {
    border-top: 1px solid rgba(0, 0, 0, 0.055);
  }

  &:hover {
    background: rgba(99, 102, 241, 0.05);
  }

  &__name {
    flex: 1 1 auto;
    min-width: 0;
    font-size: 13px;
    font-weight: 600;
  }

  &__count {
    flex: 0 0 auto;
    font-weight: 700;
    font-size: 13px;
    font-variant-numeric: tabular-nums;
  }
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.06);
  font-size: 10.5px;
  font-weight: 700;
  color: #64748b;
  flex-shrink: 0;

  &--0 {
    background: #f6d365;
    color: #7a5b00;
  }

  &--1 {
    background: #d7dde8;
    color: #4b5563;
  }

  &--2 {
    background: #d6a77a;
    color: #6b3f16;
  }
}
</style>

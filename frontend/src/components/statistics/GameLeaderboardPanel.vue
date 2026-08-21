<template>
  <div>
    <div v-if="loading" class="flex justify-center q-pa-lg">
      <q-spinner color="primary" size="32px" />
    </div>

    <template v-else-if="leaderboard">
      <div class="text-caption text-grey-6 q-mb-sm">
        {{ leaderboard.platform }}
      </div>

      <!-- Experts: the three most dominant players at this game, ranked by
           win %. Medal-colored badges (gold/silver/bronze) match the
           podium styling used for season winners. -->
      <div v-if="fameLeaders.length > 0" class="fame-card q-mb-md">
        <div class="fame-card__header row items-center no-wrap q-mb-sm">
          <q-icon name="emoji_events" size="18px" color="primary" class="q-mr-xs" />
          <span class="text-weight-bolder text-dark">Experts</span>
          <q-space />
          <span class="text-caption text-grey-6">Win %</span>
        </div>
        <div class="row q-col-gutter-sm">
          <div v-for="(leader, idx) in fameLeaders" :key="leader.profile_id" class="col">
            <div class="fame-player">
              <span class="rank-badge" :class="`rank-badge--${idx}`">{{ idx + 1 }}</span>
              <div
                class="fame-player__name ellipsis"
                :class="{ 'text-weight-bolder text-primary': leader.is_me }"
              >
                {{ leader.profile_name }}
              </div>
              <div class="fame-player__score text-weight-bolder text-dark">
                {{ leader.fameScore.toFixed(1) }}%
              </div>
            </div>
          </div>
        </div>
      </div>

      <div
        v-if="!leaderboard.me.eligible"
        class="me-row row items-center justify-between q-pa-sm q-mb-sm rounded-borders me-row--unranked"
      >
        <span class="text-weight-bold">You</span>
        <span class="text-caption text-grey-6">
          {{ leaderboard.me.games_played }} game(s) played &middot; no ranking yet
        </span>
      </div>

      <KennerTable
        v-if="leaderboard.leaderboard.length > 0"
        flat
        :rows="leaderboard.leaderboard"
        :columns="columns"
        row-key="profile_id"
      >
        <template v-slot:body-cell-profile_name="props">
          <q-td :props="props">
            <span :class="{ 'text-weight-bolder text-primary': props.row.is_me }">
              {{ props.row.profile_name }}
              <q-badge
                v-if="props.row.is_me"
                color="primary"
                text-color="white"
                class="q-ml-xs"
                label="you"
              />
            </span>
          </q-td>
        </template>
      </KennerTable>
      <div v-else class="text-caption text-grey-6 q-pa-md">
        No one has played this game yet.
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import KennerTable from 'components/tables/KennerTable.vue';
import { TGameLeaderboard } from 'src/types';

defineProps<{
  loading: boolean;
  leaderboard: TGameLeaderboard | null;
  fameLeaders: Array<{ profile_id: number; profile_name: string; is_me: boolean; fameScore: number }>;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  columns: any[];
}>();
</script>

<style scoped lang="scss">
.me-row {
  background: rgba(99, 102, 241, 0.06);
  border: 1px solid rgba(99, 102, 241, 0.15);
}

.me-row--unranked {
  background: rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(0, 0, 0, 0.06);
}

// Experts: a plain bordered panel matching the app's flat card style
// (no gradients).
.fame-card {
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
}

.fame-player {
  height: 100%;
  text-align: center;
  padding: 10px 6px 8px;
  border-radius: 8px;
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: border-color 0.15s ease;

  &:hover {
    border-color: rgba(99, 102, 241, 0.25);
  }

  &__name {
    font-size: 11.5px;
    line-height: 1.2;
    margin-top: 5px;
  }

  &__score {
    font-size: 13.5px;
    font-weight: 700;
    margin-top: 2px;
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

  &--0 {
    background: #f6d365; /* gold */
    color: #7a5b00;
  }

  &--1 {
    background: #d7dde8; /* silver */
    color: #4b5563;
  }

  &--2 {
    background: #d6a77a; /* bronze */
    color: #6b3f16;
  }
}
</style>

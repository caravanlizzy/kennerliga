<template>
  <q-card flat bordered class="rounded-borders bg-white overflow-hidden">
    <q-card-section class="q-pa-md border-bottom bg-grey-1">
      <div class="row items-center justify-between">
        <div class="text-subtitle1 text-weight-bold text-dark">
          Player Performance Rankings
        </div>
        <div class="text-caption text-grey-6">
          Ranked by Win Rate &middot; Ties broken by Average Position
        </div>
      </div>
    </q-card-section>

    <KennerTable
      v-if="leaderboard && leaderboard.length > 0"
      flat
      :rows="leaderboard"
      :columns="columns"
      row-key="profile_id"
    >
      <!-- Rank slot -->
      <template v-slot:body-cell-rank="props">
        <q-td :props="props">
          <span
            v-if="props.row.rank && props.row.rank <= 3"
            class="rank-badge"
            :class="`rank-badge--${props.row.rank - 1}`"
          >
            {{ props.row.rank }}
          </span>
          <span v-else-if="props.row.rank" class="text-weight-bold text-grey-7">
            #{{ props.row.rank }}
          </span>
          <span v-else class="text-caption text-grey-5">-</span>
        </q-td>
      </template>

      <!-- Player Name slot -->
      <template v-slot:body-cell-profile_name="props">
        <q-td :props="props">
          <div class="row items-center no-wrap">
            <span
              class="text-weight-bold"
              :class="props.row.is_me ? 'text-primary' : 'text-grey-9'"
            >
              {{ props.row.profile_name }}
            </span>
            <q-badge
              v-if="props.row.is_me"
              color="primary"
              text-color="white"
              class="q-ml-xs text-weight-bold"
              label="YOU"
            />
          </div>
        </q-td>
      </template>

      <!-- Win Rate slot -->
      <template v-slot:body-cell-win_rate="props">
        <q-td :props="props">
          <div class="row items-center no-wrap">
            <span
              class="text-weight-bolder"
              :class="
                props.row.win_rate >= 50 ? 'text-positive' : 'text-grey-8'
              "
            >
              {{ props.row.win_rate }}%
            </span>
          </div>
        </q-td>
      </template>
    </KennerTable>

    <div v-else class="text-center q-py-xl text-grey-6">
      <q-icon name="sports_esports" size="40px" class="q-mb-sm text-grey-4" />
      <div class="text-subtitle2">No match results recorded yet</div>
      <div class="text-caption">
        Results will appear here as soon as matches for this game are finished.
      </div>
    </div>
  </q-card>
</template>

<script setup lang="ts">
import KennerTable from 'components/tables/KennerTable.vue';
import type { TGameLeaderboardPlayer } from 'src/types';

defineProps<{
  leaderboard: TGameLeaderboardPlayer[];
  columns: any[];
}>();
</script>

<style scoped>
.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  font-weight: 700;
  font-size: 11px;
}
.rank-badge--0 {
  background: #ffd700;
  color: #5a4a00;
}
.rank-badge--1 {
  background: #c0c0c0;
  color: #3a3a3a;
}
.rank-badge--2 {
  background: #cd7f32;
  color: #3d2314;
}
.border-bottom {
  border-bottom: 1px solid var(--kenner-border-subtle);
}
</style>

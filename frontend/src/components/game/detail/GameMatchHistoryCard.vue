<template>
  <div v-if="matches && matches.length > 0" class="column q-gutter-y-md">
    <q-card
      v-for="match in matches"
      :key="match.id"
      flat
      bordered
      class="match-history-card rounded-borders bg-white"
    >
      <!-- Match Header -->
      <q-card-section class="q-py-sm q-px-md bg-grey-1 border-bottom">
        <div class="row items-center justify-between no-wrap">
          <div class="row items-center q-gutter-x-sm">
            <q-badge color="primary" text-color="white">
              {{ match.season_name || `Season #${match.season_id}` }}
            </q-badge>
            <q-badge color="secondary" text-color="white">
              {{
                match.league_name ||
                (match.league_level != null
                  ? `League ${match.league_level}`
                  : 'League')
              }}
            </q-badge>
            <span class="text-caption text-grey-6">
              {{ formatDate(match.date) }}
            </span>
          </div>

          <KennerButton
            flat
            dense
            no-caps
            size="sm"
            color="primary"
            icon-right="arrow_forward"
            label="Match Details"
            @click="$emit('viewMatch', match.id)"
          />
        </div>
      </q-card-section>

      <!-- Match Results Participants -->
      <q-card-section class="q-pa-md">
        <div class="row q-col-gutter-sm">
          <div
            v-for="part in match.participants"
            :key="part.profile_id"
            class="col-12 col-sm-6 col-md-4"
          >
            <div
              class="participant-item q-pa-sm rounded-borders row items-center justify-between no-wrap"
              :class="{
                'participant-item--winner': part.is_winner,
                'bg-grey-1': !part.is_winner,
              }"
            >
              <div class="row items-center no-wrap ellipsis">
                <span
                  class="rank-badge q-mr-sm"
                  :class="`rank-badge--${(part.position || 1) - 1}`"
                >
                  {{ part.position }}
                </span>
                <div class="ellipsis">
                  <div class="text-weight-bold text-body2 ellipsis">
                    {{ part.profile_name }}
                  </div>
                  <div
                    v-if="part.faction_name || part.win_condition_name"
                    class="text-caption text-grey-6"
                  >
                    {{ part.faction_name || part.win_condition_name }}
                  </div>
                </div>
              </div>

              <div
                v-if="part.points !== null"
                class="text-weight-bolder text-right"
              >
                <span
                  :class="part.is_winner ? 'text-deep-orange-9' : 'text-grey-8'"
                >
                  {{ part.points }}
                </span>
                <span class="text-caption text-grey-6 q-ml-xs">pts</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Selected Options Chips (if any) -->
        <div
          v-if="match.selected_options && match.selected_options.length > 0"
          class="row items-center q-gutter-xs q-mt-sm"
        >
          <span class="text-caption text-grey-6 q-mr-xs">Rules:</span>
          <q-chip
            v-for="(opt, oIdx) in match.selected_options"
            :key="oIdx"
            dense
            size="sm"
            color="grey-2"
            text-color="grey-8"
          >
            <span class="text-weight-bold q-mr-xs">{{ opt.option_name }}:</span>
            <span>{{ opt.choice_name }}</span>
          </q-chip>
        </div>
      </q-card-section>
    </q-card>
  </div>

  <div v-else class="text-center q-py-xl text-grey-6 bg-white rounded-borders">
    <q-icon name="history" size="40px" class="q-mb-sm text-grey-4" />
    <div class="text-subtitle2">No matches played yet</div>
  </div>
</template>

<script setup lang="ts">
import KennerButton from 'components/base/KennerButton.vue';
import type { TGameMatch } from 'src/types';

defineProps<{
  matches: TGameMatch[];
  formatDate: (dateStr?: string) => string;
}>();

defineEmits<{
  (e: 'viewMatch', matchId: number): void;
}>();
</script>

<style scoped>
.border-bottom {
  border-bottom: 1px solid var(--kenner-border-subtle);
}
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
.participant-item {
  border: 1px solid var(--kenner-border-subtle);
}
.participant-item--winner {
  background: rgba(255, 193, 7, 0.12);
  border-color: rgba(255, 193, 7, 0.4);
}
</style>

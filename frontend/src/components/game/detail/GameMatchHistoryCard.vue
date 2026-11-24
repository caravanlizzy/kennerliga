<template>
  <q-card flat bordered class="rounded-borders bg-white overflow-hidden">
    <q-card-section class="q-pa-md border-bottom bg-grey-1">
      <div class="row items-center justify-between">
        <div class="text-subtitle1 text-weight-bold text-dark">Matches</div>
        <div class="text-caption text-grey-6">
          {{ matches ? matches.length : 0 }} recorded
          {{ matches && matches.length === 1 ? 'match' : 'matches' }}
        </div>
      </div>
    </q-card-section>

    <KennerTable
      v-if="matches && matches.length > 0"
      flat
      :rows="matches"
      :columns="columns"
      row-key="id"
      class="cursor-pointer"
      @row-click="(_evt, row) => $emit('viewMatch', row.id)"
    >
      <!-- Season slot -->
      <template v-slot:body-cell-season="props">
        <q-td :props="props">
          <div class="row items-center no-wrap">
            <q-icon
              name="event"
              color="secondary"
              size="18px"
              class="q-mr-xs shrink-0"
            />
            <span class="text-weight-medium">
              {{
                props.row.season_name ||
                (props.row.season_id ? `Season #${props.row.season_id}` : '-')
              }}
            </span>
          </div>
        </q-td>
      </template>

      <!-- League slot -->
      <template v-slot:body-cell-league="props">
        <q-td :props="props">
          <span class="text-weight-medium">
            {{
              props.row.league_name ||
              (props.row.league_level != null
                ? `League ${props.row.league_level}`
                : '-')
            }}
          </span>
        </q-td>
      </template>

      <!-- Date slot -->
      <template v-slot:body-cell-date="props">
        <q-td :props="props">
          <span class="text-caption text-grey-7">
            {{ formatDate(props.row.date) }}
          </span>
        </q-td>
      </template>

      <!-- Players slot -->
      <template v-slot:body-cell-players="props">
        <q-td :props="props">
          <div class="row items-center q-gutter-xs">
            <q-badge
              v-for="part in props.row.participants"
              :key="part.profile_id"
              :color="part.is_winner ? 'amber-2' : 'grey-2'"
              :text-color="part.is_winner ? 'amber-10' : 'grey-9'"
              class="q-pa-xs text-weight-medium"
            >
              <q-icon
                v-if="part.is_winner"
                name="emoji_events"
                size="12px"
                class="q-mr-xs text-amber-9"
              />
              {{ part.profile_name }}
              <span
                v-if="part.points !== null"
                class="q-ml-xs text-weight-bold"
              >
                ({{ part.points }} pts)
              </span>
            </q-badge>
          </div>
        </q-td>
      </template>

      <!-- Factions slot -->
      <template v-slot:body-cell-factions="props">
        <q-td :props="props">
          <div
            v-if="hasFactions(props.row)"
            class="row items-center q-gutter-xs"
          >
            <q-badge
              v-for="part in getParticipantFactions(props.row)"
              :key="part.profile_id"
              color="deep-purple-1"
              text-color="deep-purple-8"
              class="q-pa-xs text-weight-medium"
            >
              <q-icon name="shield" size="12px" class="q-mr-xs shrink-0" />
              <span>{{ part.faction_name || part.win_condition_name }}</span>
              <span class="text-caption text-grey-6 q-ml-xs">
                ({{ part.profile_name }})
              </span>
            </q-badge>
          </div>
          <span v-else class="text-caption text-grey-5">-</span>
        </q-td>
      </template>

      <!-- Actions slot -->
      <template v-slot:body-cell-actions="props">
        <q-td :props="props" align="right">
          <KennerButton
            flat
            dense
            no-caps
            size="sm"
            color="primary"
            icon="visibility"
            :label="isMobile ? undefined : 'View'"
            @click.stop="$emit('viewMatch', props.row.id)"
          />
        </q-td>
      </template>
    </KennerTable>

    <div v-else class="text-center q-py-xl text-grey-6">
      <q-icon name="history" size="40px" class="q-mb-sm text-grey-4" />
      <div class="text-subtitle2">No matches played yet</div>
      <div class="text-caption">
        Matches for this game will appear here once results are submitted.
      </div>
    </div>
  </q-card>
</template>

<script setup lang="ts">
import KennerTable from 'components/tables/KennerTable.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { useResponsive } from 'src/composables/responsive';
import type { TGameRecentMatch } from 'src/types';

const { isMobile } = useResponsive();

defineProps<{
  matches: TGameRecentMatch[];
  columns: any[];
  formatDate: (dateStr?: string) => string;
}>();

defineEmits<{
  (e: 'viewMatch', matchId: number): void;
}>();

function hasFactions(match: TGameRecentMatch): boolean {
  return (
    Boolean(match.participants) &&
    match.participants.some((p) =>
      Boolean(p.faction_name || p.win_condition_name)
    )
  );
}

function getParticipantFactions(match: TGameRecentMatch) {
  return (match.participants || []).filter((p) =>
    Boolean(p.faction_name || p.win_condition_name)
  );
}
</script>

<style scoped>
.border-bottom {
  border-bottom: 1px solid var(--kenner-border-subtle);
}
.shrink-0 {
  flex-shrink: 0;
}
</style>

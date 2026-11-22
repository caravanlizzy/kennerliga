<template>
  <div class="column q-gutter-y-lg">
    <!-- Faction Performance Table (if factions exist) -->
    <q-card
      v-if="factions && factions.length > 0"
      flat
      bordered
      class="rounded-borders bg-white overflow-hidden"
    >
      <q-card-section class="q-pa-md border-bottom bg-grey-1">
        <div class="row items-center justify-between">
          <div class="text-subtitle1 text-weight-bold text-dark">
            Faction Performance &amp; Win Rates
          </div>
          <div class="text-caption text-grey-6">
            {{ factions.length }} configured factions
          </div>
        </div>
      </q-card-section>

      <KennerTable flat :rows="factions" :columns="columns" row-key="id">
        <template v-slot:body-cell-win_rate="props">
          <q-td :props="props">
            <span
              class="text-weight-bold"
              :class="
                props.row.win_rate >= 50 ? 'text-positive' : 'text-grey-8'
              "
            >
              {{ props.row.win_rate }}%
            </span>
          </q-td>
        </template>
      </KennerTable>
    </q-card>

    <!-- Game Configuration Summary Card -->
    <q-card flat bordered class="rounded-borders bg-white">
      <q-card-section
        class="q-pa-md border-bottom bg-grey-1 row items-center justify-between"
      >
        <div class="text-subtitle1 text-weight-bold text-dark">
          Game Rules &amp; Options Configuration
        </div>
        <KennerButton
          v-if="isAdmin"
          flat
          dense
          no-caps
          size="sm"
          color="primary"
          icon="settings"
          label="Edit in Admin Config"
          @click="$emit('editConfig', game.id)"
        />
      </q-card-section>

      <q-card-section class="q-pa-md">
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-6">
            <div
              class="text-caption text-weight-bold text-grey-7 text-uppercase q-mb-xs"
            >
              Scoring &amp; Mechanics
            </div>
            <q-list
              dense
              separator
              class="rounded-borders border-light bg-grey-1"
            >
              <q-item>
                <q-item-section>Points-based Scoring</q-item-section>
                <q-item-section side>
                  <q-badge :color="game.has_points ? 'positive' : 'grey-6'">
                    {{ game.has_points ? 'Yes' : 'No' }}
                  </q-badge>
                </q-item-section>
              </q-item>
              <q-item>
                <q-item-section>Asymmetric Factions</q-item-section>
                <q-item-section side>
                  <q-badge :color="game.is_asymmetric ? 'purple' : 'grey-6'">
                    {{ game.is_asymmetric ? 'Yes' : 'No' }}
                  </q-badge>
                </q-item-section>
              </q-item>
              <q-item>
                <q-item-section>Starting Player Order</q-item-section>
                <q-item-section side>
                  <q-badge
                    :color="
                      game.has_starting_player_order ? 'positive' : 'grey-6'
                    "
                  >
                    {{ game.has_starting_player_order ? 'Yes' : 'No' }}
                  </q-badge>
                </q-item-section>
              </q-item>
              <q-item v-if="game.starting_points_system">
                <q-item-section>Starting Points System</q-item-section>
                <q-item-section side class="text-weight-medium text-dark">
                  {{ game.starting_points_system }}
                </q-item-section>
              </q-item>
            </q-list>
          </div>

          <div class="col-12 col-md-6">
            <div
              class="text-caption text-weight-bold text-grey-7 text-uppercase q-mb-xs"
            >
              Configured Options &amp; Variants
            </div>
            <div v-if="game.options && game.options.length > 0">
              <div
                v-for="opt in game.options"
                :key="opt.id"
                class="q-mb-sm q-pa-sm rounded-borders bg-grey-1 border-light"
              >
                <div class="text-weight-bold text-body2 text-grey-9">
                  {{ opt.name }}
                </div>
                <div
                  v-if="opt.choices && opt.choices.length > 0"
                  class="row items-center q-gutter-xs q-mt-xs"
                >
                  <q-chip
                    v-for="(c, cIdx) in opt.choices"
                    :key="cIdx"
                    dense
                    size="xs"
                    color="white"
                    text-color="grey-8"
                    class="border-light"
                  >
                    {{ c }}
                  </q-chip>
                </div>
                <div v-else class="text-caption text-grey-6">
                  Binary toggle (Yes / No)
                </div>
              </div>
            </div>
            <div
              v-else
              class="text-caption text-grey-6 q-pa-sm bg-grey-1 rounded-borders"
            >
              No variant options configured for this game.
            </div>
          </div>
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import KennerTable from 'components/tables/KennerTable.vue';
import KennerButton from 'components/base/KennerButton.vue';
import type { TGameDto, TGameFactionStat } from 'src/types';

defineProps<{
  factions: TGameFactionStat[];
  columns: any[];
  game: TGameDto;
  isAdmin: boolean;
}>();

defineEmits<{
  (e: 'editConfig', gameId: number): void;
}>();
</script>

<style scoped>
.border-bottom {
  border-bottom: 1px solid var(--kenner-border-subtle);
}
.border-light {
  border: 1px solid var(--kenner-border-subtle);
}
</style>

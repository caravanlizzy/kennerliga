<template>
  <div class="column q-gutter-y-lg">
    <!-- 1. Starting Player Order / Turn Order Impact Analysis Card -->
    <q-card
      v-if="
        (startingPositions && startingPositions.length > 0) ||
        game.has_starting_player_order
      "
      flat
      bordered
      class="rounded-borders bg-white overflow-hidden"
    >
      <q-card-section class="q-pa-md border-bottom bg-grey-1">
        <div class="row items-center justify-between">
          <div class="row items-center q-gutter-x-sm">
            <q-icon name="format_list_numbered" size="20px" color="secondary" />
            <div class="text-subtitle1 text-weight-bold text-dark">
              Starting Player Order Impact
            </div>
          </div>
          <div class="text-caption text-grey-6">
            {{ startingPositions ? startingPositions.length : 0 }} tracked
            positions
          </div>
        </div>
      </q-card-section>

      <!-- Starting Order Insight Banner -->
      <q-card-section
        v-if="topStartingPosition"
        class="q-pa-md bg-secondary-subtle border-bottom"
      >
        <div class="row items-center no-wrap">
          <q-icon
            name="lightbulb"
            color="secondary"
            size="22px"
            class="q-mr-sm shrink-0"
          />
          <div class="text-body2 text-grey-9">
            <span class="text-weight-bold text-secondary">
              Seat #{{ topStartingPosition.starting_position }} ({{
                getOrdinal(topStartingPosition.starting_position)
              }}
              Player)
            </span>
            has the highest win rate at
            <span class="text-weight-bold"
              >{{ topStartingPosition.win_rate }}%</span
            >
            ({{ topStartingPosition.wins }} wins out of
            {{ topStartingPosition.games_played }} games).
          </div>
        </div>
      </q-card-section>

      <KennerTable
        v-if="startingPositions && startingPositions.length > 0"
        flat
        :rows="startingPositions"
        :columns="startingPositionColumns"
        row-key="starting_position"
      >
        <!-- Seat slot -->
        <template v-slot:body-cell-starting_position="props">
          <q-td :props="props">
            <div class="row items-center no-wrap">
              <q-badge
                color="secondary"
                text-color="white"
                class="q-px-xs text-caption text-weight-bold q-mr-sm"
              >
                #{{ props.row.starting_position }}
              </q-badge>
              <span class="text-weight-medium">
                {{ getOrdinal(props.row.starting_position) }} Player
              </span>
            </div>
          </q-td>
        </template>

        <!-- Win Rate slot -->
        <template v-slot:body-cell-win_rate="props">
          <q-td :props="props">
            <div class="row items-center q-gutter-x-sm no-wrap">
              <span
                class="text-weight-bold"
                :class="
                  props.row.win_rate >= 40
                    ? 'text-positive'
                    : props.row.win_rate >= 25
                    ? 'text-secondary'
                    : 'text-grey-8'
                "
              >
                {{ props.row.win_rate }}%
              </span>
              <q-linear-progress
                :value="props.row.win_rate / 100"
                :color="
                  props.row.win_rate >= 40
                    ? 'positive'
                    : props.row.win_rate >= 25
                    ? 'secondary'
                    : 'grey-6'
                "
                track-color="grey-3"
                rounded
                style="width: 60px; height: 6px"
              />
            </div>
          </q-td>
        </template>

        <!-- Record slot -->
        <template v-slot:body-cell-record="props">
          <q-td :props="props" align="center">
            <span class="text-weight-medium text-dark">
              {{ props.row.wins }} / {{ props.row.games_played }}
            </span>
          </q-td>
        </template>

        <!-- Avg Position slot -->
        <template v-slot:body-cell-avg_position="props">
          <q-td :props="props" align="center">
            <span class="text-weight-medium">
              {{
                props.row.avg_position !== null ? props.row.avg_position : '-'
              }}
            </span>
          </q-td>
        </template>

        <!-- Avg Points slot -->
        <template v-slot:body-cell-avg_points="props">
          <q-td :props="props" align="center">
            <span class="text-weight-medium">
              {{ props.row.avg_points !== null ? props.row.avg_points : '-' }}
            </span>
          </q-td>
        </template>

        <!-- Best Score slot -->
        <template v-slot:body-cell-best_score="props">
          <q-td :props="props" align="center">
            <span class="text-weight-bold text-amber-10">
              {{ props.row.best_score !== null ? props.row.best_score : '-' }}
            </span>
          </q-td>
        </template>
      </KennerTable>

      <div v-else class="text-center q-py-lg text-grey-6">
        <q-icon
          name="format_list_numbered"
          size="32px"
          class="q-mb-xs text-grey-4"
        />
        <div class="text-caption">
          Starting order statistics will populate as matches are recorded.
        </div>
      </div>
    </q-card>

    <!-- 2. Faction Performance Table (if factions exist) -->
    <q-card
      v-if="factions && factions.length > 0"
      flat
      bordered
      class="rounded-borders bg-white overflow-hidden"
    >
      <q-card-section class="q-pa-md border-bottom bg-grey-1">
        <div class="row items-center justify-between">
          <div class="row items-center q-gutter-x-sm">
            <q-icon name="shield" size="20px" color="deep-purple-7" />
            <div class="text-subtitle1 text-weight-bold text-dark">
              Faction Performance &amp; Win Rates
            </div>
          </div>
          <div class="text-caption text-grey-6">
            {{ factions.length }} configured factions
          </div>
        </div>
      </q-card-section>

      <!-- Faction Insight Banner -->
      <q-card-section
        v-if="topFaction"
        class="q-pa-md bg-purple-subtle border-bottom"
      >
        <div class="row items-center no-wrap">
          <q-icon
            name="emoji_events"
            color="deep-purple-7"
            size="22px"
            class="q-mr-sm shrink-0"
          />
          <div class="text-body2 text-grey-9">
            <span class="text-weight-bold text-deep-purple-9">
              {{ topFaction.name }}
            </span>
            leads faction win rates with
            <span class="text-weight-bold">{{ topFaction.win_rate }}%</span>
            ({{ topFaction.wins }} wins in {{ topFaction.games_played }} games).
          </div>
        </div>
      </q-card-section>

      <KennerTable
        flat
        :rows="factions"
        :columns="factionTableColumns"
        row-key="id"
      >
        <template v-slot:body-cell-name="props">
          <q-td :props="props">
            <div class="row items-center no-wrap">
              <q-icon
                name="shield"
                color="deep-purple-6"
                size="16px"
                class="q-mr-xs shrink-0"
              />
              <span class="text-weight-bold text-dark">{{
                props.row.name
              }}</span>
            </div>
          </q-td>
        </template>

        <template v-slot:body-cell-win_rate="props">
          <q-td :props="props">
            <div class="row items-center q-gutter-x-sm no-wrap">
              <span
                class="text-weight-bold"
                :class="
                  props.row.win_rate >= 50
                    ? 'text-positive'
                    : props.row.win_rate >= 30
                    ? 'text-deep-purple-9'
                    : 'text-grey-8'
                "
              >
                {{ props.row.win_rate }}%
              </span>
              <q-linear-progress
                :value="props.row.win_rate / 100"
                :color="
                  props.row.win_rate >= 50
                    ? 'positive'
                    : props.row.win_rate >= 30
                    ? 'deep-purple-6'
                    : 'grey-6'
                "
                track-color="grey-3"
                rounded
                style="width: 50px; height: 6px"
              />
            </div>
          </q-td>
        </template>

        <template v-slot:body-cell-record="props">
          <q-td :props="props" align="center">
            <span class="text-weight-medium text-dark">
              {{ props.row.wins }} / {{ props.row.games_played }}
            </span>
          </q-td>
        </template>
      </KennerTable>
    </q-card>

    <!-- 3. Rule Variants & Options Performance Table (if variants exist) -->
    <q-card
      v-if="ruleVariants && ruleVariants.length > 0"
      flat
      bordered
      class="rounded-borders bg-white overflow-hidden"
    >
      <q-card-section class="q-pa-md border-bottom bg-grey-1">
        <div class="row items-center justify-between">
          <div class="row items-center q-gutter-x-sm">
            <q-icon name="tune" size="20px" color="primary" />
            <div class="text-subtitle1 text-weight-bold text-dark">
              Rule Variants &amp; Options Breakdown
            </div>
          </div>
          <div class="text-caption text-grey-6">
            {{ ruleVariants.length }} variant combinations recorded
          </div>
        </div>
      </q-card-section>

      <KennerTable
        flat
        :rows="ruleVariants"
        :columns="ruleVariantColumns"
        row-key="choice_id"
      >
        <template v-slot:body-cell-choice_name="props">
          <q-td :props="props">
            <q-chip
              dense
              size="sm"
              color="primary"
              text-color="white"
              class="text-weight-medium"
            >
              {{ props.row.choice_name }}
            </q-chip>
          </q-td>
        </template>
      </KennerTable>
    </q-card>

    <!-- 4. Game Configuration Summary Card -->
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
import { computed } from 'vue';
import KennerTable from 'components/tables/KennerTable.vue';
import KennerButton from 'components/base/KennerButton.vue';
import type {
  TGameDetailInfo,
  TGameFactionStat,
  TGameStartingPositionStat,
  TGameRuleVariantStat,
} from 'src/types';

const props = defineProps<{
  factions: TGameFactionStat[];
  startingPositions?: TGameStartingPositionStat[];
  ruleVariants?: TGameRuleVariantStat[];
  game: TGameDetailInfo;
  isAdmin: boolean;
}>();

defineEmits<{
  (e: 'editConfig', gameId: number): void;
}>();

function getOrdinal(n: number): string {
  const s = ['th', 'st', 'nd', 'rd'];
  const v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
}

const topStartingPosition = computed(() => {
  const list = props.startingPositions || [];
  const playedList = list.filter((s) => s.games_played > 0);
  if (playedList.length === 0) return null;
  return [...playedList].sort(
    (a, b) => b.win_rate - a.win_rate || b.games_played - a.games_played
  )[0];
});

const topFaction = computed(() => {
  const list = props.factions || [];
  const playedList = list.filter((f) => f.games_played > 0);
  if (playedList.length === 0) return null;
  return [...playedList].sort(
    (a, b) => b.win_rate - a.win_rate || b.games_played - a.games_played
  )[0];
});

const startingPositionColumns = [
  {
    name: 'starting_position',
    label: 'Turn Order / Seat',
    field: (r: TGameStartingPositionStat) => r.starting_position,
    align: 'left',
    sortable: true,
  },
  {
    name: 'win_rate',
    label: 'Win Rate',
    field: (r: TGameStartingPositionStat) => r.win_rate,
    align: 'left',
    sortable: true,
  },
  {
    name: 'record',
    label: 'Wins / Games',
    field: (r: TGameStartingPositionStat) => `${r.wins} / ${r.games_played}`,
    align: 'center',
    sortable: true,
  },
  {
    name: 'avg_position',
    label: 'Avg Finish Rank',
    field: (r: TGameStartingPositionStat) =>
      r.avg_position !== null ? r.avg_position : '-',
    align: 'center',
    sortable: true,
  },
  {
    name: 'avg_points',
    label: 'Avg Points',
    field: (r: TGameStartingPositionStat) =>
      r.avg_points !== null ? r.avg_points : '-',
    align: 'center',
    sortable: true,
  },
  {
    name: 'best_score',
    label: 'High Score',
    field: (r: TGameStartingPositionStat) =>
      r.best_score !== null ? r.best_score : '-',
    align: 'center',
    sortable: true,
  },
];

const factionTableColumns = [
  {
    name: 'name',
    label: 'Faction',
    field: (r: TGameFactionStat) => r.name,
    align: 'left',
    sortable: true,
  },
  {
    name: 'win_rate',
    label: 'Win Rate',
    field: (r: TGameFactionStat) => r.win_rate,
    align: 'left',
    sortable: true,
  },
  {
    name: 'record',
    label: 'Wins / Matches',
    field: (r: TGameFactionStat) => `${r.wins} / ${r.games_played}`,
    align: 'center',
    sortable: true,
  },
  {
    name: 'avg_position',
    label: 'Avg Position',
    field: (r: TGameFactionStat) =>
      r.avg_position !== null ? r.avg_position : '-',
    align: 'center',
    sortable: true,
  },
  {
    name: 'avg_points',
    label: 'Avg Points',
    field: (r: TGameFactionStat) =>
      r.avg_points !== null ? r.avg_points : '-',
    align: 'center',
    sortable: true,
  },
  {
    name: 'best_score',
    label: 'Best Score',
    field: (r: TGameFactionStat) =>
      r.best_score !== null ? r.best_score : '-',
    align: 'center',
    sortable: true,
  },
];

const ruleVariantColumns = [
  {
    name: 'option_name',
    label: 'Rule Option',
    field: (r: TGameRuleVariantStat) => r.option_name,
    align: 'left',
    sortable: true,
  },
  {
    name: 'choice_name',
    label: 'Choice / Variant',
    field: (r: TGameRuleVariantStat) => r.choice_name,
    align: 'left',
    sortable: true,
  },
  {
    name: 'matches_count',
    label: 'Matches Played',
    field: (r: TGameRuleVariantStat) => r.matches_count,
    align: 'center',
    sortable: true,
  },
  {
    name: 'avg_winning_score',
    label: 'Avg Winning Score',
    field: (r: TGameRuleVariantStat) =>
      r.avg_winning_score !== null ? r.avg_winning_score : '-',
    align: 'center',
    sortable: true,
  },
  {
    name: 'avg_score',
    label: 'Avg Score',
    field: (r: TGameRuleVariantStat) =>
      r.avg_score !== null ? r.avg_score : '-',
    align: 'center',
    sortable: true,
  },
  {
    name: 'high_score',
    label: 'High Score',
    field: (r: TGameRuleVariantStat) =>
      r.high_score !== null ? r.high_score : '-',
    align: 'center',
    sortable: true,
  },
];
</script>

<style scoped>
.border-bottom {
  border-bottom: 1px solid var(--kenner-border-subtle);
}
.border-light {
  border: 1px solid var(--kenner-border-subtle);
}
.shrink-0 {
  flex-shrink: 0;
}
.bg-secondary-subtle {
  background-color: rgba(38, 166, 154, 0.08);
}
.bg-purple-subtle {
  background-color: rgba(103, 58, 183, 0.08);
}
</style>

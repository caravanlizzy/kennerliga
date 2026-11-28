<template>
  <div class="column q-gutter-y-md">
    <!-- Search & Filter Mask Card -->
    <q-card flat bordered class="rounded-borders bg-white">
      <q-card-section class="q-pa-md border-bottom bg-grey-1">
        <div class="row items-center justify-between q-col-gutter-sm">
          <div class="row items-center q-gutter-x-sm">
            <q-icon name="filter_alt" size="20px" color="primary" />
            <div class="text-subtitle1 text-weight-bold text-dark">
              Search &amp; Filter Matches
            </div>
            <q-badge
              v-if="activeFilterCount > 0"
              color="primary"
              text-color="white"
              rounded
              class="q-px-xs text-caption"
            >
              {{ activeFilterCount }} active
            </q-badge>
          </div>

          <div class="row items-center q-gutter-x-xs">
            <KennerButton
              v-if="activeFilterCount > 0"
              flat
              dense
              no-caps
              size="sm"
              color="negative"
              icon="clear"
              label="Reset"
              @click="resetFilters"
            />
            <KennerButton
              flat
              dense
              no-caps
              size="sm"
              :color="showFilterPanel ? 'primary' : 'grey-7'"
              :icon="showFilterPanel ? 'expand_less' : 'expand_more'"
              :label="showFilterPanel ? 'Hide Filters' : 'Show Filters'"
              @click="showFilterPanel = !showFilterPanel"
            />
          </div>
        </div>
      </q-card-section>

      <!-- Search & Filters Body -->
      <q-slide-transition>
        <q-card-section v-show="showFilterPanel" class="q-pa-md">
          <div class="row q-col-gutter-sm items-center">
            <!-- Text Search -->
            <div class="col-12 col-md-4">
              <q-input
                v-model="searchQuery"
                dense
                outlined
                placeholder="Search player, faction, season..."
                clearable
                class="bg-white"
              >
                <template #prepend>
                  <q-icon name="search" size="18px" />
                </template>
              </q-input>
            </div>

            <!-- Faction Filter -->
            <div
              v-if="factionOptions.length > 1"
              class="col-12 col-sm-6 col-md-3"
            >
              <q-select
                v-model="selectedFaction"
                dense
                outlined
                emit-value
                map-options
                :options="factionOptions"
                label="Faction"
                class="bg-white"
              >
                <template #prepend>
                  <q-icon name="shield" size="18px" color="purple-7" />
                </template>
              </q-select>
            </div>

            <!-- Player Filter -->
            <div
              v-if="playerOptions.length > 1"
              class="col-12 col-sm-6 col-md-3"
            >
              <q-select
                v-model="selectedPlayer"
                dense
                outlined
                emit-value
                map-options
                :options="playerOptions"
                label="Player"
                class="bg-white"
              >
                <template #prepend>
                  <q-icon name="person" size="18px" color="primary" />
                </template>
              </q-select>
            </div>

            <!-- Season Filter -->
            <div
              v-if="seasonOptions.length > 1"
              class="col-12 col-sm-6 col-md-3"
            >
              <q-select
                v-model="selectedSeason"
                dense
                outlined
                emit-value
                map-options
                :options="seasonOptions"
                label="Season"
                class="bg-white"
              >
                <template #prepend>
                  <q-icon name="event" size="18px" color="secondary" />
                </template>
              </q-select>
            </div>

            <!-- Winner Only Toggle -->
            <div class="col-12 col-sm-6 col-md-3">
              <q-checkbox
                v-model="onlyWinnerMatches"
                dense
                label="Only matches where selection won"
                color="amber-9"
                class="text-caption text-weight-medium"
                :disable="!selectedPlayer && !selectedFaction"
              />
            </div>
          </div>
        </q-card-section>
      </q-slide-transition>
    </q-card>

    <!-- Quick Properties & Performance Insights Ribbon -->
    <div v-if="matches && matches.length > 0" class="row q-col-gutter-sm">
      <!-- Total Matches Found -->
      <div class="col-12 col-sm-6 col-md-3">
        <q-card
          flat
          bordered
          class="rounded-borders bg-white q-pa-sm full-height"
        >
          <div class="row items-center no-wrap">
            <q-avatar
              size="32px"
              color="primary"
              text-color="white"
              icon="history"
              class="q-mr-sm shrink-0"
            />
            <div>
              <div class="text-caption text-grey-6">Matches Shown</div>
              <div class="text-subtitle2 text-weight-bold">
                {{ filteredMatches.length }}
                <span
                  v-if="filteredMatches.length !== matches.length"
                  class="text-caption text-grey-6"
                >
                  / {{ matches.length }}
                </span>
              </div>
            </div>
          </div>
        </q-card>
      </div>

      <!-- Top Winning Starting Seat -->
      <div class="col-12 col-sm-6 col-md-3">
        <q-card
          flat
          bordered
          class="rounded-borders bg-white q-pa-sm full-height"
        >
          <div class="row items-center no-wrap">
            <q-avatar
              size="32px"
              color="secondary"
              text-color="white"
              icon="event_seat"
              class="q-mr-sm shrink-0"
            />
            <div class="ellipsis">
              <div class="text-caption text-grey-6">Top Starting Order</div>
              <div
                class="text-subtitle2 text-weight-bold text-secondary ellipsis"
              >
                <template v-if="topSeatInsight">
                  Seat {{ topSeatInsight.seat }} ({{ topSeatInsight.winRate }}%
                  wins)
                </template>
                <template v-else> N/A </template>
              </div>
            </div>
          </div>
        </q-card>
      </div>

      <!-- Top Winning Faction -->
      <div class="col-12 col-sm-6 col-md-3">
        <q-card
          flat
          bordered
          class="rounded-borders bg-white q-pa-sm full-height"
        >
          <div class="row items-center no-wrap">
            <q-avatar
              size="32px"
              color="deep-purple-7"
              text-color="white"
              icon="shield"
              class="q-mr-sm shrink-0"
            />
            <div class="ellipsis">
              <div class="text-caption text-grey-6">Top Faction</div>
              <div
                class="text-subtitle2 text-weight-bold text-deep-purple-9 ellipsis"
              >
                <template v-if="topFactionInsight">
                  {{ topFactionInsight.name }} ({{ topFactionInsight.wins }}
                  wins)
                </template>
                <template v-else> N/A </template>
              </div>
            </div>
          </div>
        </q-card>
      </div>

      <!-- Average Winning Score -->
      <div class="col-12 col-sm-6 col-md-3">
        <q-card
          flat
          bordered
          class="rounded-borders bg-white q-pa-sm full-height"
        >
          <div class="row items-center no-wrap">
            <q-avatar
              size="32px"
              color="amber-9"
              text-color="white"
              icon="emoji_events"
              class="q-mr-sm shrink-0"
            />
            <div>
              <div class="text-caption text-grey-6">Avg Winning Score</div>
              <div class="text-subtitle2 text-weight-bold text-amber-10">
                {{ avgWinningScore !== null ? `${avgWinningScore} pts` : '-' }}
              </div>
            </div>
          </div>
        </q-card>
      </div>
    </div>

    <!-- Matches Table Card -->
    <q-card flat bordered class="rounded-borders bg-white overflow-hidden">
      <q-card-section class="q-pa-md border-bottom bg-grey-1">
        <div class="row items-center justify-between">
          <div class="text-subtitle1 text-weight-bold text-dark">
            Match History &amp; Statistical Breakdown
          </div>
          <div class="text-caption text-grey-6">
            {{ filteredMatches.length }}
            {{ filteredMatches.length === 1 ? 'match' : 'matches' }}
          </div>
        </div>
      </q-card-section>

      <KennerTable
        v-if="filteredMatches && filteredMatches.length > 0"
        flat
        :rows="filteredMatches"
        :columns="tableColumns"
        row-key="id"
        class="cursor-pointer"
        @row-click="(_evt, row) => $emit('viewMatch', row.id)"
      >
        <!-- Season & League slot -->
        <template v-slot:body-cell-season="props">
          <q-td :props="props">
            <div class="column q-gutter-y-xs">
              <div class="row items-center no-wrap">
                <q-icon
                  name="event"
                  color="secondary"
                  size="15px"
                  class="q-mr-xs shrink-0"
                />
                <span class="text-weight-medium text-dark">
                  {{
                    props.row.season_name ||
                    (props.row.season_id
                      ? `Season #${props.row.season_id}`
                      : '-')
                  }}
                </span>
              </div>
              <span class="text-caption text-grey-7">
                {{
                  props.row.league_name ||
                  (props.row.league_level != null
                    ? `League ${props.row.league_level}`
                    : '-')
                }}
              </span>
            </div>
          </q-td>
        </template>

        <!-- Winner slot -->
        <template v-slot:body-cell-winner="props">
          <q-td :props="props">
            <div
              v-if="getWinner(props.row)"
              class="row items-center no-wrap q-gutter-x-xs"
            >
              <q-badge
                color="amber-2"
                text-color="amber-10"
                class="q-pa-xs text-weight-bolder"
              >
                <q-icon
                  name="emoji_events"
                  size="13px"
                  class="q-mr-xs text-amber-9"
                />
                {{ getWinner(props.row)?.profile_name }}
                <span
                  v-if="
                    getWinner(props.row)?.points !== null &&
                    getWinner(props.row)?.points !== undefined
                  "
                  class="q-ml-xs text-dark"
                >
                  ({{ getWinner(props.row)?.points }} pts)
                </span>
              </q-badge>

              <q-badge
                v-if="getWinner(props.row)?.starting_position"
                color="secondary"
                text-color="white"
                class="q-px-xs text-caption"
              >
                Seat #{{ getWinner(props.row)?.starting_position }}
              </q-badge>

              <q-badge
                v-if="getWinner(props.row)?.faction_name"
                color="deep-purple-1"
                text-color="deep-purple-8"
                class="q-px-xs text-caption"
              >
                {{ getWinner(props.row)?.faction_name }}
              </q-badge>
            </div>
            <span v-else class="text-caption text-grey-5">-</span>
          </q-td>
        </template>

        <!-- Standings / Players slot -->
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
                <span
                  class="rank-indicator q-mr-xs"
                  :class="{ 'rank-indicator--winner': part.is_winner }"
                >
                  {{ part.position || '-' }}
                </span>
                {{ part.profile_name }}
                <span
                  v-if="part.starting_position"
                  class="text-caption text-grey-6 q-ml-xs"
                >
                  [Seat {{ part.starting_position }}]
                </span>
                <span
                  v-if="part.points !== null && part.points !== undefined"
                  class="q-ml-xs text-weight-bold"
                >
                  ({{ part.points }})
                </span>
              </q-badge>
            </div>
          </q-td>
        </template>

        <!-- Starting Order slot -->
        <template v-slot:body-cell-starting_order="props">
          <q-td :props="props">
            <div
              v-if="hasStartingPositions(props.row)"
              class="column items-start q-gutter-y-xs"
            >
              <q-badge
                v-for="part in getSortedByStartingOrder(props.row)"
                :key="part.profile_id"
                :color="part.is_winner ? 'amber-1' : 'grey-1'"
                :text-color="part.is_winner ? 'amber-10' : 'grey-8'"
                class="q-pa-xs border-subtle"
              >
                <span class="text-weight-bolder q-mr-xs text-secondary">
                  #{{ part.starting_position }}:
                </span>
                <span>{{ part.profile_name }}</span>
                <q-icon
                  v-if="part.is_winner"
                  name="emoji_events"
                  size="12px"
                  class="q-ml-xs text-amber-9"
                />
              </q-badge>
            </div>
            <span v-else class="text-caption text-grey-5">-</span>
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
                <span>{{ part.faction_name }}</span>
                <span class="text-caption text-grey-6 q-ml-xs">
                  ({{ part.profile_name }})
                </span>
              </q-badge>
            </div>
            <span v-else class="text-caption text-grey-5">-</span>
          </q-td>
        </template>

        <!-- Rules & Variants slot -->
        <template v-slot:body-cell-rules="props">
          <q-td :props="props">
            <div
              v-if="
                props.row.selected_options &&
                props.row.selected_options.length > 0
              "
              class="row items-center q-gutter-xs"
            >
              <q-chip
                v-for="(opt, oIdx) in props.row.selected_options"
                :key="oIdx"
                dense
                size="xs"
                color="grey-2"
                text-color="grey-8"
              >
                <span class="text-weight-bold q-mr-xs"
                  >{{ opt.option_name }}:</span
                >
                <span>{{ opt.choice_name }}</span>
              </q-chip>
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

      <!-- Empty state when filtered -->
      <div
        v-else-if="matches && matches.length > 0"
        class="text-center q-py-xl text-grey-6"
      >
        <q-icon
          name="filter_list_off"
          size="40px"
          class="q-mb-sm text-grey-4"
        />
        <div class="text-subtitle2">No matches match your filter criteria</div>
        <div class="text-caption q-mb-md">
          Try clearing or adjusting your search filters.
        </div>
        <KennerButton
          outline
          dense
          no-caps
          size="sm"
          color="primary"
          icon="refresh"
          label="Reset Filters"
          @click="resetFilters"
        />
      </div>

      <!-- Empty state when no matches exist -->
      <div v-else class="text-center q-py-xl text-grey-6">
        <q-icon name="history" size="40px" class="q-mb-sm text-grey-4" />
        <div class="text-subtitle2">No matches played yet</div>
        <div class="text-caption">
          Matches for this game will appear here once results are submitted.
        </div>
      </div>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import KennerTable from 'components/tables/KennerTable.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { useResponsive } from 'src/composables/responsive';
import type { TGameRecentMatch, TGameMatchParticipant } from 'src/types';

const { isMobile } = useResponsive();

const props = defineProps<{
  matches: TGameRecentMatch[];
  initialPlayer?: number | string | null;
}>();

defineEmits<{
  (e: 'viewMatch', matchId: number): void;
}>();

// Filter states
const showFilterPanel = ref(true);
const searchQuery = ref('');
const selectedFaction = ref<string | null>(null);
const selectedPlayer = ref<number | null>(null);
const selectedSeason = ref<string | null>(null);
const onlyWinnerMatches = ref(false);

function applyInitialPlayer() {
  if (props.initialPlayer != null && props.initialPlayer !== '') {
    const numericId = Number(props.initialPlayer);
    if (!isNaN(numericId) && numericId > 0) {
      selectedPlayer.value = numericId;
    } else {
      const found = playerOptions.value.find(
        (opt) =>
          opt.label.toLowerCase() === String(props.initialPlayer).toLowerCase()
      );
      if (found && found.value != null) {
        selectedPlayer.value = found.value;
      }
    }
  }
}

watch(
  [() => props.initialPlayer, () => playerOptions.value],
  () => {
    if (props.initialPlayer != null && props.initialPlayer !== '') {
      applyInitialPlayer();
    }
  },
  { immediate: true }
);

const activeFilterCount = computed(() => {
  let count = 0;
  if (searchQuery.value?.trim()) count++;
  if (selectedFaction.value) count++;
  if (selectedPlayer.value) count++;
  if (selectedSeason.value) count++;
  if (onlyWinnerMatches.value) count++;
  return count;
});

function resetFilters() {
  searchQuery.value = '';
  selectedFaction.value = null;
  selectedPlayer.value = null;
  selectedSeason.value = null;
  onlyWinnerMatches.value = false;
}

// Extract filter options from match data
const factionOptions = computed(() => {
  const factionSet = new Set<string>();
  (props.matches || []).forEach((m) => {
    (m.participants || []).forEach((p) => {
      if (p.faction_name) factionSet.add(p.faction_name);
    });
  });
  const list = Array.from(factionSet).sort();
  return [
    { label: 'All Factions', value: null },
    ...list.map((f) => ({ label: f, value: f })),
  ];
});

const playerOptions = computed(() => {
  const map = new Map<number, string>();
  (props.matches || []).forEach((m) => {
    (m.participants || []).forEach((p) => {
      map.set(p.profile_id, p.profile_name);
    });
  });
  const list = Array.from(map.entries())
    .map(([id, name]) => ({ label: name, value: id }))
    .sort((a, b) => a.label.localeCompare(b.label));
  return [{ label: 'All Players', value: null }, ...list];
});

const seasonOptions = computed(() => {
  const seasonSet = new Set<string>();
  (props.matches || []).forEach((m) => {
    if (m.season_name) seasonSet.add(m.season_name);
    else if (m.season_id) seasonSet.add(`Season #${m.season_id}`);
  });
  const list = Array.from(seasonSet).sort();
  return [
    { label: 'All Seasons', value: null },
    ...list.map((s) => ({ label: s, value: s })),
  ];
});

// Filtered matches
const filteredMatches = computed(() => {
  const list = props.matches || [];
  return list.filter((m) => {
    // Text search query
    if (searchQuery.value && searchQuery.value.trim() !== '') {
      const q = searchQuery.value.toLowerCase().trim();
      const seasonText = (
        m.season_name || `Season #${m.season_id || ''}`
      ).toLowerCase();
      const leagueText = (
        m.league_name || `League ${m.league_level || ''}`
      ).toLowerCase();
      const matchParticipants = (m.participants || []).some(
        (p) =>
          p.profile_name.toLowerCase().includes(q) ||
          (p.faction_name && p.faction_name.toLowerCase().includes(q))
      );
      const matchOptions = (m.selected_options || []).some(
        (o) =>
          o.option_name.toLowerCase().includes(q) ||
          o.choice_name.toLowerCase().includes(q)
      );
      if (
        !seasonText.includes(q) &&
        !leagueText.includes(q) &&
        !matchParticipants &&
        !matchOptions
      ) {
        return false;
      }
    }

    // Faction filter
    if (selectedFaction.value) {
      const matchFaction = (m.participants || []).some((p) => {
        const hasFaction = p.faction_name === selectedFaction.value;
        return onlyWinnerMatches.value ? hasFaction && p.is_winner : hasFaction;
      });
      if (!matchFaction) return false;
    }

    // Player filter
    if (selectedPlayer.value !== null) {
      const matchPlayer = (m.participants || []).some((p) => {
        const isPlayer = p.profile_id === selectedPlayer.value;
        return onlyWinnerMatches.value ? isPlayer && p.is_winner : isPlayer;
      });
      if (!matchPlayer) return false;
    }

    // Season filter
    if (selectedSeason.value) {
      const seasonLabel = m.season_name || `Season #${m.season_id || ''}`;
      if (seasonLabel !== selectedSeason.value) return false;
    }

    return true;
  });
});

// Dynamic property insight calculations
const topSeatInsight = computed(() => {
  const matchesList = filteredMatches.value;
  if (!matchesList || matchesList.length === 0) return null;

  const seatWins = new Map<number, number>();
  let totalWithSeat = 0;

  matchesList.forEach((m) => {
    const winner = (m.participants || []).find((p) => p.is_winner);
    if (winner && winner.starting_position) {
      seatWins.set(
        winner.starting_position,
        (seatWins.get(winner.starting_position) || 0) + 1
      );
      totalWithSeat++;
    }
  });

  if (totalWithSeat === 0 || seatWins.size === 0) return null;

  let bestSeat = 1;
  let maxWins = -1;
  seatWins.forEach((wins, seat) => {
    if (wins > maxWins) {
      maxWins = wins;
      bestSeat = seat;
    }
  });

  return {
    seat: bestSeat,
    wins: maxWins,
    winRate: Math.round((maxWins / totalWithSeat) * 100),
  };
});

const topFactionInsight = computed(() => {
  const matchesList = filteredMatches.value;
  if (!matchesList || matchesList.length === 0) return null;

  const factionWins = new Map<string, number>();
  matchesList.forEach((m) => {
    const winner = (m.participants || []).find((p) => p.is_winner);
    if (winner && winner.faction_name) {
      factionWins.set(
        winner.faction_name,
        (factionWins.get(winner.faction_name) || 0) + 1
      );
    }
  });

  if (factionWins.size === 0) return null;

  let bestFaction = '';
  let maxWins = -1;
  factionWins.forEach((wins, name) => {
    if (wins > maxWins) {
      maxWins = wins;
      bestFaction = name;
    }
  });

  return {
    name: bestFaction,
    wins: maxWins,
  };
});

const avgWinningScore = computed(() => {
  const matchesList = filteredMatches.value;
  if (!matchesList || matchesList.length === 0) return null;

  const winningScores: number[] = [];
  matchesList.forEach((m) => {
    const winner = (m.participants || []).find((p) => p.is_winner);
    if (winner && winner.points !== null && winner.points !== undefined) {
      winningScores.push(winner.points);
    }
  });

  if (winningScores.length === 0) return null;
  const sum = winningScores.reduce((acc, v) => acc + v, 0);
  return Math.round((sum / winningScores.length) * 10) / 10;
});

// Helper functions for rows
function getWinner(match: TGameRecentMatch): TGameMatchParticipant | undefined {
  return (match.participants || []).find((p) => p.is_winner);
}

function hasStartingPositions(match: TGameRecentMatch): boolean {
  return (
    Boolean(match.participants) &&
    match.participants.some((p) => Boolean(p.starting_position))
  );
}

function getSortedByStartingOrder(
  match: TGameRecentMatch
): TGameMatchParticipant[] {
  return [...(match.participants || [])]
    .filter((p) => Boolean(p.starting_position))
    .sort((a, b) => (a.starting_position || 99) - (b.starting_position || 99));
}

function hasFactions(match: TGameRecentMatch): boolean {
  return (
    Boolean(match.participants) &&
    match.participants.some((p) => Boolean(p.faction_name))
  );
}

function getParticipantFactions(match: TGameRecentMatch) {
  return (match.participants || []).filter((p) => Boolean(p.faction_name));
}

// Table columns
const tableColumns = computed(() => [
  {
    name: 'season',
    label: 'Season / League',
    field: (r: TGameRecentMatch) =>
      r.season_name || (r.season_id ? `Season #${r.season_id}` : '-'),
    align: 'left',
    sortable: true,
  },
  {
    name: 'winner',
    label: 'Winner',
    field: (r: TGameRecentMatch) => getWinner(r)?.profile_name || '-',
    align: 'left',
    sortable: true,
  },
  {
    name: 'players',
    label: 'Standings & Players',
    field: (r: TGameRecentMatch) =>
      r.participants?.map((p) => p.profile_name).join(', ') || '-',
    align: 'left',
    sortable: false,
  },
  {
    name: 'starting_order',
    label: 'Turn Order',
    field: (r: TGameRecentMatch) =>
      getSortedByStartingOrder(r)
        .map((p) => `#${p.starting_position}: ${p.profile_name}`)
        .join(', ') || '-',
    align: 'left',
    sortable: false,
  },
  {
    name: 'factions',
    label: 'Factions',
    field: (r: TGameRecentMatch) =>
      r.participants
        ?.map((p) => p.faction_name)
        .filter(Boolean)
        .join(', ') || '-',
    align: 'left',
    sortable: false,
  },
  {
    name: 'rules',
    label: 'Options',
    field: (r: TGameRecentMatch) =>
      r.selected_options
        ?.map((o) => `${o.option_name}: ${o.choice_name}`)
        .join(', ') || '-',
    align: 'left',
    sortable: false,
  },
  {
    name: 'actions',
    label: '',
    field: () => '',
    align: 'right',
  },
]);
</script>

<style scoped>
.border-bottom {
  border-bottom: 1px solid var(--kenner-border-subtle);
}
.border-subtle {
  border: 1px solid var(--kenner-border-subtle);
}
.shrink-0 {
  flex-shrink: 0;
}
.rank-indicator {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  font-weight: 700;
  font-size: 10px;
  background: #e0e0e0;
  color: #424242;
}
.rank-indicator--winner {
  background: #ffd700;
  color: #5a4a00;
}
</style>

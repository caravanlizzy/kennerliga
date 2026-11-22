<template>
  <KennerTable
    v-if="!loading && !error && data && Array.isArray(data)"
    title="Match Results"
    flat
    row-key="id"
    :rows="data"
    :columns="columns"
    :pagination="pagination"
    @row-click="onRowClick"
    class="cursor-pointer"
  >
    <template v-slot:body-cell-game="props">
      <q-td :props="props">
        <div class="row items-center no-wrap">
          <q-icon
            name="sports_esports"
            color="primary"
            size="20px"
            class="q-mr-sm shrink-0"
          />
          <span
            class="text-weight-bold text-subtitle2 ellipsis"
            :style="{ maxWidth: isMobile ? '130px' : '200px' }"
          >
            {{
              truncateString(
                props.row.game_name || `Game #${props.row.game}`,
                isMobile ? 16 : 24
              )
            }}
            <KennerTooltip
              v-if="(props.row.game_name || '').length > (isMobile ? 16 : 24)"
            >
              {{ props.row.game_name }}
            </KennerTooltip>
          </span>
          <q-badge
            v-if="hasRecord(props.row)"
            color="deep-orange-1"
            text-color="deep-orange-9"
            class="q-ml-sm shrink-0 stat-badge text-weight-bolder"
          >
            <q-icon
              name="local_fire_department"
              size="12px"
              class="q-mr-xs text-deep-orange-6"
            />
            RECORD
            <KennerTooltip>
              This match contains an all-time record score!
            </KennerTooltip>
          </q-badge>
          <q-badge
            v-if="props.row.platform_name"
            color="grey-3"
            text-color="grey-8"
            class="q-ml-sm shrink-0"
          >
            {{ props.row.platform_name }}
          </q-badge>
        </div>
      </q-td>
    </template>

    <template v-slot:body-cell-season="props">
      <q-td :props="props">
        <div class="row items-center no-wrap">
          <q-icon name="event" color="secondary" size="18px" class="q-mr-xs" />
          <span class="text-weight-medium">
            {{
              props.row.season_name ||
              (props.row.season_id ? `Season #${props.row.season_id}` : '-')
            }}
          </span>
        </div>
      </q-td>
    </template>

    <template v-slot:body-cell-players="props">
      <q-td :props="props">
        <div
          v-if="getPlayers(props.row).length > 0"
          class="row items-center q-gutter-xs"
        >
          <q-badge
            v-for="(player, idx) in getPlayers(props.row)"
            :key="idx"
            :color="
              player.is_record
                ? 'deep-orange-1'
                : player.position === 1
                ? 'amber-2'
                : 'grey-2'
            "
            :text-color="
              player.is_record
                ? 'deep-orange-9'
                : player.position === 1
                ? 'amber-10'
                : 'grey-9'
            "
            class="q-pa-xs text-weight-medium"
            :class="{ 'record-badge-glow': player.is_record }"
          >
            <q-icon
              v-if="player.is_record"
              name="local_fire_department"
              size="12px"
              class="q-mr-xs text-deep-orange-6"
            />
            <q-icon
              v-else-if="player.position === 1"
              name="emoji_events"
              size="12px"
              class="q-mr-xs text-amber-9"
            />
            {{ player.name }}
            <span
              v-if="player.points != null && props.row.has_points !== false"
              class="q-ml-xs text-weight-bold"
            >
              ({{ player.points }})
            </span>
            <KennerTooltip v-if="player.is_record">
              All-time record score: {{ player.points }} VP!
            </KennerTooltip>
          </q-badge>
        </div>
        <div v-else class="text-grey-5">-</div>
      </q-td>
    </template>

    <template v-slot:body-cell-actions="props">
      <q-td :props="props" class="q-gutter-x-sm" @click.stop>
        <KennerButton
          dense
          outline
          no-caps
          color="primary"
          icon="visibility"
          :label="isMobile ? undefined : 'View'"
          :to="{ name: 'match-result-detail', params: { id: props.row.id } }"
        />
      </q-td>
    </template>
  </KennerTable>

  <div v-else class="q-py-md">
    <q-banner v-if="error" rounded dense class="q-mb-sm">
      <template #avatar><q-icon name="warning" color="negative" /></template>
      {{ error }}
    </q-banner>
    <q-skeleton v-else height="220px" square />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import type { QTableProps } from 'quasar';
import KennerTable from 'components/tables/KennerTable.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import { truncateString } from 'src/helpers';
import { useAsyncData } from 'src/composables/asyncData';
import { fetchSelectedGames } from 'src/services/gameService';
import { useResponsive } from 'src/composables/responsive';
import type { TSelectedGameDto } from 'src/types';

const router = useRouter();
const { isMobile } = useResponsive();

const pagination = ref({
  rowsPerPage: 20,
});

const {
  data,
  isFinished,
  error: fetchError,
} = useAsyncData<TSelectedGameDto[]>(
  () => fetchSelectedGames({ has_results: true }),
  []
);

const loading = computed(() => !isFinished.value);
const error = computed(() => fetchError?.value?.message || null);

function hasRecord(row: TSelectedGameDto): boolean {
  return row.results?.some((r) => r.is_record) ?? false;
}

function getPlayers(row: TSelectedGameDto): {
  name: string;
  position?: number | null;
  points?: number | null;
  is_record?: boolean;
}[] {
  if (!row.results || row.results.length === 0) return [];
  return [...row.results]
    .sort((a, b) => (a.position ?? 999) - (b.position ?? 999))
    .map((r) => ({
      name:
        r.player_profile_name ||
        (r.player_profile ? `Player #${r.player_profile}` : 'Unknown'),
      position: r.position,
      points: r.points,
      is_record: r.is_record,
    }));
}

function onRowClick(_evt: unknown, row: TSelectedGameDto) {
  router.push({ name: 'match-result-detail', params: { id: row.id } });
}

const columns = computed<QTableProps['columns']>(() => [
  {
    name: 'season',
    label: 'Season',
    field: (r: TSelectedGameDto) =>
      r.season_name || (r.season_id ? `Season #${r.season_id}` : '-'),
    align: 'left',
    sortable: true,
  },
  {
    name: 'game',
    label: 'Game',
    field: (r: TSelectedGameDto) => r.game_name || `Game #${r.game}`,
    align: 'left',
    sortable: true,
  },
  {
    name: 'league',
    label: 'League',
    field: (r: TSelectedGameDto) =>
      r.league_level != null ? `League ${r.league_level}` : '-',
    align: 'left',
    sortable: true,
  },
  {
    name: 'players',
    label: 'Players',
    field: (r: TSelectedGameDto) =>
      getPlayers(r)
        .map((p) => p.name)
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

<style scoped lang="scss">
.stat-badge {
  padding: 2px 6px;
  font-size: 11px;
  border-radius: 4px;
}

.record-badge-glow {
  border: 1px solid rgba(249, 115, 22, 0.4) !important;
  box-shadow: 0 0 6px rgba(249, 115, 22, 0.15);
}

.cursor-pointer :deep(tbody tr) {
  cursor: pointer;
}
</style>

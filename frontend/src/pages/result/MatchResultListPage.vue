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
            style="max-width: 200px"
          >
            {{ truncateString(props.row.game_name || `Game #${props.row.game}`, 24) }}
            <KennerTooltip v-if="(props.row.game_name || '').length > 24">
              {{ props.row.game_name }}
            </KennerTooltip>
          </span>
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
            {{ props.row.season_name || (props.row.season_id ? `Season #${props.row.season_id}` : '-') }}
          </span>
        </div>
      </q-td>
    </template>

    <template v-slot:body-cell-players="props">
      <q-td :props="props">
        <div v-if="getPlayers(props.row).length > 0" class="row items-center q-gutter-xs">
          <q-badge
            v-for="(player, idx) in getPlayers(props.row)"
            :key="idx"
            :color="player.position === 1 ? 'amber-2' : 'grey-2'"
            :text-color="player.position === 1 ? 'amber-10' : 'grey-9'"
            class="q-pa-xs text-weight-medium"
          >
            <q-icon
              v-if="player.position === 1"
              name="emoji_events"
              size="12px"
              class="q-mr-xs text-amber-9"
            />
            {{ player.name }}
          </q-badge>
        </div>
        <div v-else class="text-grey-5">-</div>
      </q-td>
    </template>

    <template v-slot:body-cell-winner="props">
      <q-td :props="props">
        <div v-if="getWinner(props.row)" class="row items-center no-wrap text-amber-9">
          <q-icon name="emoji_events" size="18px" class="q-mr-xs" />
          <span class="text-weight-bold">{{ getWinner(props.row) }}</span>
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
} = useAsyncData<TSelectedGameDto[]>(() => fetchSelectedGames({ has_results: true }), []);

const loading = computed(() => !isFinished.value);
const error = computed(() => fetchError?.value?.message || null);

function getWinner(row: TSelectedGameDto): string | null {
  if (!row.results || row.results.length === 0) return null;
  const winner = row.results.find((r) => r.position === 1);
  return winner?.player_profile_name || null;
}

function getPlayers(
  row: TSelectedGameDto
): { name: string; position?: number | null }[] {
  if (!row.results || row.results.length === 0) return [];
  return [...row.results]
    .sort((a, b) => (a.position ?? 999) - (b.position ?? 999))
    .map((r) => ({
      name: r.player_profile_name || `Player #${r.player_profile}`,
      position: r.position,
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
    name: 'winner',
    label: 'Winner',
    field: (r: TSelectedGameDto) => getWinner(r) || '-',
    align: 'left',
    sortable: true,
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
.cursor-pointer :deep(tbody tr) {
  cursor: pointer;
}
</style>

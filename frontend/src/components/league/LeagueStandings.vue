<template>
  <div>
    <!-- Unresolved Tie Info (only when all league games are finished) -->
    <div
      v-if="leagueId && allGamesFinished && tieGroups.some(g => g.unresolved)"
      class="q-mb-md"
    >
      <div class="unresolved-card">
        <div class="unresolved-card__header">
          <q-icon name="emoji_events" size="18px" class="unresolved-card__icon" />
          <div class="unresolved-card__title">Unresolved tie</div>
          <q-badge class="unresolved-card__badge" rounded>
            {{ tieGroups.filter(g => g.unresolved).length }}
          </q-badge>
          <q-btn
            v-if="adminMode"
            label="Resolve"
            size="xs"
            color="primary"
            unelevated
            class="q-ml-auto"
            @click="emit('resolve-tie', tieGroups.find(g => g.unresolved))"
          />
        </div>
        <div class="unresolved-card__body">
          <div
            v-for="grp in tieGroups.filter(g => g.unresolved)"
            :key="grp.group_key"
            class="unresolved-card__group"
          >
            <template v-for="(m, idx) in grp.members" :key="m.player_profile_id">
              <span class="unresolved-card__player">{{ m.profile_name }}</span>
              <span
                v-if="idx < grp.members.length - 1"
                class="unresolved-card__vs"
              >vs</span>
            </template>
          </div>
        </div>
        <div class="unresolved-card__hint">
          Awaiting tie-break decision.
        </div>
      </div>
    </div>

    <q-table
      v-if="rows.length > 0"
      flat
      :rows="rows"
      :columns="columns"
      row-key="player_profile"
      hide-bottom
      class="bg-transparent"
      :loading="loading"
    >
      <template #body-cell-profile_name="props">
        <q-td :props="props">
          <div class="row items-center no-wrap">
            {{ props.value }}
            <template v-if="props.row.unresolved_tie_group">
              <span class="text-orange q-ml-xs cursor-pointer" style="font-size: 1.1rem; line-height: 1;">
                *
                <q-tooltip>unresolved tie</q-tooltip>
              </span>
            </template>
            <template v-else-if="props.row.resolved_tie_reason">
              <span class="text-green q-ml-xs cursor-pointer" style="font-size: 1.1rem; line-height: 1;">
                *
                <q-tooltip>{{ props.row.resolved_tie_reason }}</q-tooltip>
              </span>
            </template>
          </div>
        </q-td>
      </template>
    </q-table>
    <div v-else-if="!loading" class="q-pa-md text-center text-grey-6 italic">
      No standings available.
    </div>
    <div v-else-if="loading" class="q-pa-md flex flex-center">
      <q-spinner-puff color="primary" size="40px" />
    </div>

    <!-- Tie Groups Info (Shown at bottom for resolved groups or standalone) -->
    <div v-if="tieGroups.some(g => !g.unresolved) || !leagueId" class="q-mt-md q-px-md">
      <div v-if="tieGroups.some(g => !g.unresolved)" class="text-caption text-grey-8 q-mb-xs text-weight-bold">Resolved Ties</div>
      <div v-for="group in tieGroups" :key="group.group_key" class="q-mb-sm">
        <q-card flat bordered class="bg-grey-1">
          <q-card-section class="q-pa-xs">
            <div class="row items-center q-gutter-x-sm">
              <q-badge :color="group.unresolved ? 'orange' : 'green'" style="font-size: 0.5rem">
                {{ group.unresolved ? 'UNRESOLVED' : 'RESOLVED' }}
              </q-badge>
              <div class="text-caption" style="font-size: 0.7rem">
                {{ group.members.map(m => m.profile_name).join(' vs ') }}
              </div>
              <q-btn
                v-if="adminMode && group.unresolved"
                label="Resolve"
                size="xs"
                color="primary"
                flat
                dense
                class="q-ml-auto"
                @click="emit('resolve-tie', group)"
              />
            </div>
            <div v-if="group.resolution" class="text-grey-7 q-ml-sm" style="font-size: 0.65rem">
              Reason: {{ group.resolution.reason_display }}
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.border-orange-2 {
  border: 1px solid #ffcc80;
}

.unresolved-card {
  position: relative;
  border-radius: 12px;
  padding: 14px 16px;
  background: linear-gradient(135deg, #fff7ed 0%, #fff1de 100%);
  border: 1px solid #fcd9a8;
  box-shadow: 0 2px 6px rgba(180, 100, 0, 0.08);
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background: linear-gradient(180deg, #f59e0b, #d97706);
  }

  &__header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
  }

  &__icon {
    color: #d97706;
  }

  &__title {
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.3px;
    text-transform: uppercase;
    color: #92400e;
  }

  &__badge {
    background: #d97706;
    color: #fff;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 2px 8px;
  }

  &__body {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 12px;
  }

  &__group {
    display: inline-flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
    padding: 6px 10px;
    background: rgba(255, 255, 255, 0.75);
    border: 1px solid rgba(217, 119, 6, 0.25);
    border-radius: 999px;
  }

  &__player {
    font-size: 0.8rem;
    font-weight: 600;
    color: #7c2d12;
  }

  &__vs {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #b45309;
    opacity: 0.75;
  }

  &__hint {
    margin-top: 8px;
    font-size: 0.7rem;
    color: #92400e;
    opacity: 0.8;
    font-style: italic;
  }
}

</style>

<script setup lang="ts">
import { QTableProps } from 'quasar';
import { storeToRefs } from 'pinia';
import { computed, ref, onMounted } from 'vue';
import { useLeagueStore } from 'stores/leagueStore';
import { useUserStore } from 'stores/userStore';
import { api } from 'boot/axios';
import { formatNumbers } from 'src/helpers';
import { useResponsive } from 'src/composables/responsive';

const props = defineProps<{
  leagueId?: number;
  adminMode?: boolean;
}>();

const emit = defineEmits(['resolve-tie']);

const { user } = storeToRefs(useUserStore());
const myLeagueStore = computed(() => {
  const id = props.leagueId || user.value?.myCurrentLeagueId;
  return id ? useLeagueStore(id)() : null;
});
const storeLeagueId = computed(() => myLeagueStore.value?.leagueId);
const { isMobile } = useResponsive();

interface LeagueStanding {
  player_profile: number;
  profile_name: string;
  wins: number;
  league_points: number;
  unresolved_tie_group?: string;
  resolved_tie_reason?: string;
}

interface TieGroup {
  group_key: string;
  unresolved: boolean;
  members: Array<{
    player_profile_id: number;
    profile_name: string;
    user_id?: number;
    username?: string;
  }>;
  resolution?: {
    reason_display: string;
    note?: string;
  };
}

interface FullStandingsResponse {
  standings: any[];
  tie_groups: TieGroup[];
  all_games_finished?: boolean;
}

const standings = ref<LeagueStanding[]>([]);
const tieGroups = ref<TieGroup[]>([]);
const allGamesFinished = ref(false);
const loading = ref(false);

const fetchStandings = async () => {
  const idToUse = props.leagueId || storeLeagueId.value;
  if (!idToUse) return;
  loading.value = true;
  try {
    const { data } = await api.get<FullStandingsResponse>(
      `league/leagues/${idToUse}/full-standings/`
    );
    // Transform full-standings to LeagueStanding format
    standings.value = data.standings.map(s => {
      const group = data.tie_groups?.find(g => g.group_key === s.unresolved_tie_group);
      return {
        player_profile: s.player_profile_id,
        profile_name: s.profile_name,
        wins: parseFloat(s.total_wins || '0'),
        league_points: parseFloat(s.total_league_points || '0'),
        unresolved_tie_group: s.unresolved_tie_group,
        resolved_tie_reason: (group && !group.unresolved) ? group.resolution?.reason_display : undefined
      };
    });
    tieGroups.value = data.tie_groups || [];
    allGamesFinished.value = !!data.all_games_finished;
  } catch (e) {
    console.error('Error fetching standings:', e);
  } finally {
    loading.value = false;
  }
};

onMounted(fetchStandings);

const rows = computed(() => {
  return [...standings.value].sort((a, b) => {
    if (b.league_points !== a.league_points)
      return b.league_points - a.league_points;
    if (b.wins !== a.wins) return b.wins - a.wins;
    return a.profile_name.localeCompare(b.profile_name);
  });
});

const columns: QTableProps['columns'] = [
  {
    name: 'profile_name',
    label: 'Player',
    field: 'profile_name',
    align: 'left',
  },
  {
    name: 'league_points',
    label: 'League Points',
    field: 'league_points',
    align: 'center',
    format: (val: number) => formatNumbers(val),
  },
  {
    name: 'wins',
    label: 'Wins',
    field: 'wins',
    align: 'center',
    format: (val: number) => formatNumbers(val),
  },
];
</script>

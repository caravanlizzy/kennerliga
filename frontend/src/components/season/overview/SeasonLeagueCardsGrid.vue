<template>
  <div :class="isMobile ? 'column q-px-md q-gutter-y-sm' : 'league-cards-grid'">
    <div
      v-for="league in sortedLeagues"
      :key="league.id"
      class="league-overview-card"
      :class="{
        'league-overview-card--user': isUserInLeague(league.id),
        'league-overview-card--mobile': isMobile,
      }"
    >
      <!-- Card Header -->
      <div class="row items-center justify-between no-wrap q-gutter-x-sm">
        <div class="row items-center q-gutter-x-xs no-wrap ellipsis col">
          <LeagueLevel :level="league.level" badge />
          <span class="text-subtitle1 text-weight-bold text-dark ellipsis">
            {{ leagueDisplayName(league) }}
          </span>
          <div
            v-if="isUserInLeague(league.id)"
            class="user-league-pill row items-center no-wrap shrink-0"
          >
            <q-icon name="person" size="13px" class="q-mr-xs" />
            <span>Your League</span>
          </div>
          <q-badge
            v-if="league.status"
            :color="leagueStatusColor(league.status)"
            class="text-weight-bold text-caption text-uppercase q-px-xs shrink-0"
            rounded
          >
            {{ league.status }}
          </q-badge>
        </div>
        <KennerButton
          outline
          dense
          no-caps
          size="sm"
          color="primary"
          icon-right="arrow_forward"
          label="View"
          class="q-px-sm shrink-0"
          @click="$emit('selectLeague', league.id)"
        />
      </div>

      <!-- League Meta -->
      <div
        class="row items-center q-gutter-x-md text-caption text-grey-7 q-py-xs"
      >
        <div class="row items-center q-gutter-x-xs">
          <q-icon name="groups" size="17px" color="grey-6" />
          <span>{{ getMembersForLeague(league.id).length }} players</span>
        </div>
      </div>

      <!-- Standings Table -->
      <div
        v-if="standingsMap[league.id]?.standings?.length"
        class="column q-gutter-y-xs q-mt-xs"
      >
        <div
          v-for="(row, rIdx) in standingsMap[league.id].standings"
          :key="row.player_profile_id"
          class="standings-mini-row row items-center justify-between no-wrap q-py-xs q-px-sm rounded-borders"
          :class="{
            'standings-mini-row--leader': !isMobile && rIdx === 0,
            'standings-mini-row--user': isCurrentUser(
              row.player_profile_id,
              row.username
            ),
          }"
        >
          <div
            class="row items-center q-gutter-x-xs no-wrap ellipsis col q-mr-xs"
          >
            <span
              class="rank-badge text-caption text-weight-bold shrink-0"
              :class="rIdx === 0 ? 'text-amber-9' : 'text-grey-7'"
            >
              {{ rIdx + 1 }}.
            </span>
            <UserAvatar
              :display-username="row.username"
              :subtitle="row.profile_name"
              :shape="
                getMemberShape(league.id, row.player_profile_id, row.username)
              "
              :color="
                getMemberColor(league.id, row.player_profile_id, row.username)
              "
              size="22px"
            />
            <span class="ellipsis text-caption text-weight-medium">
              {{ row.profile_name || row.username }}
            </span>
          </div>
          <div
            class="text-caption text-weight-bold shrink-0"
            :class="rIdx === 0 ? 'text-amber-10' : 'text-primary'"
          >
            {{ formatPoints(row.total_league_points) }} pts
          </div>
        </div>
      </div>

      <!-- Fallback: Participants preview -->
      <div v-else class="column q-gutter-y-xs q-mt-xs">
        <div class="text-caption text-grey-6">Participants</div>
        <div class="row items-center wrap q-gutter-xs">
          <div
            v-for="m in getMembersForLeague(league.id)"
            :key="m.id"
            class="row items-center q-gutter-x-xs bg-grey-1 rounded-borders q-px-sm q-py-xs text-caption"
          >
            <UserAvatar
              :display-username="m.username"
              :subtitle="m.profile_name"
              :shape="getMemberShape(league.id, m.profile, m.username)"
              :color="getMemberColor(league.id, m.profile, m.username)"
              size="22px"
            />
            <span
              class="text-weight-medium text-grey-8 ellipsis"
              style="max-width: 90px"
            >
              {{ m.profile_name || m.username }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import LeagueLevel from 'components/season/LeagueLevel.vue';
import UserAvatar from 'components/ui/UserAvatar.vue';
import KennerButton from 'components/base/KennerButton.vue';
import type {
  TLeagueDto,
  TSeasonLeagueStandings,
  TSeasonParticipantDto,
} from 'src/types';

defineProps<{
  sortedLeagues: TLeagueDto[];
  standingsMap: Record<number, TSeasonLeagueStandings>;
  isMobile: boolean;
  isUserInLeague: (leagueId: number) => boolean;
  leagueDisplayName: (league: TLeagueDto) => string;
  leagueStatusColor: (status: string) => string;
  getMembersForLeague: (leagueId: number) => TSeasonParticipantDto[];
  getMemberShape: (
    leagueId: number,
    playerProfileId?: number,
    username?: string
  ) => string | undefined;
  getMemberColor: (
    leagueId: number,
    playerProfileId?: number,
    username?: string
  ) => string | undefined;
  isCurrentUser: (playerProfileId?: number, username?: string) => boolean;
  formatPoints: (pts: number | string | undefined | null) => string;
}>();

defineEmits<{
  (e: 'selectLeague', leagueId: number): void;
}>();
</script>

<style scoped>
.shrink-0 {
  flex-shrink: 0;
}
.league-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}
.league-overview-card {
  background: var(--kenner-card-bg, #ffffff);
  border: 1px solid var(--kenner-border-subtle);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}
.league-overview-card--mobile {
  padding: 12px 14px;
}
.body--dark .league-overview-card {
  background: var(--kenner-surface-card, #1e293b);
  border-color: var(--kenner-border-subtle);
}
.league-overview-card--user {
  border-color: rgba(var(--q-primary-rgb, 25, 118, 210), 0.4);
  box-shadow: 0 0 0 1px rgba(var(--q-primary-rgb, 25, 118, 210), 0.15);
}
.standings-mini-row {
  background: var(--kenner-surface-subtle, #f8fafc);
}
.body--dark .standings-mini-row {
  background: rgba(255, 255, 255, 0.03);
}
.standings-mini-row--leader {
  background: rgba(255, 193, 7, 0.12);
}
.standings-mini-row--user {
  background: rgba(var(--q-primary-rgb, 25, 118, 210), 0.1);
  font-weight: 600;
}
.rank-badge {
  min-width: 18px;
}
.user-league-pill {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 10px;
  background: rgba(var(--q-primary-rgb, 25, 118, 210), 0.12);
  color: var(--q-primary);
}
</style>

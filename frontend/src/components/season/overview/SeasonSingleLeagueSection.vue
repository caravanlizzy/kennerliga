<template>
  <div class="league-focused-view column q-gutter-y-md">
    <!-- League Header Info -->
    <div
      class="row items-center justify-between wrap q-py-sm border-bottom-subtle"
      :class="isMobile ? 'q-px-md' : 'q-px-xs'"
    >
      <div class="row items-center q-gutter-x-sm">
        <LeagueLevel :level="activeLeague.level" />
        <div>
          <div class="row items-center q-gutter-xs wrap">
            <span
              class="text-subtitle1 text-sm-h6 text-weight-bold text-dark"
            >
              {{ leagueDisplayName(activeLeague) }}
            </span>
            <div
              v-if="isUserInLeague(activeLeague.id)"
              class="user-league-pill row items-center no-wrap shrink-0"
            >
              <q-icon name="person" size="13px" class="q-mr-xs" />
              <span>Your League</span>
            </div>
            <q-badge
              v-if="activeLeague.status"
              :color="leagueStatusColor(activeLeague.status)"
              class="text-weight-bold text-caption text-uppercase q-px-xs q-px-sm-sm"
              rounded
            >
              {{ activeLeague.status }}
            </q-badge>
          </div>
          <div class="text-caption text-grey-7 q-mt-xs">
            {{ activeLeagueMembers.length }} Participants
          </div>
        </div>
      </div>

      <!-- Member Avatars Preview -->
      <div
        class="row items-center wrap q-gutter-xs q-mt-xs-sm q-mt-sm-none"
      >
        <UserAvatar
          v-for="m in activeLeagueMembers"
          :key="m.id"
          :display-username="m.username"
          :subtitle="m.profile_name"
          :shape="getMemberShape(activeLeague.id, m.profile, m.username)"
          :color="getMemberColor(activeLeague.id, m.profile, m.username)"
          :size="isMobile ? '28px' : '34px'"
        />
      </div>
    </div>

    <!-- Standings Matrix View -->
    <div
      v-if="activeLeagueView === 'standings' || activeLeagueView === 'all'"
      class="league-section"
    >
      <div
        v-if="activeLeagueView === 'all'"
        class="row items-center q-gutter-x-sm q-py-xs"
        :class="isMobile ? 'q-px-md' : 'q-px-xs'"
      >
        <q-icon name="grid_view" color="primary" size="20px" />
        <span class="text-subtitle1 text-weight-bold text-dark"
          >Standings Matrix</span
        >
      </div>
      <div :class="isMobile ? 'q-px-none' : 'q-px-xs'">
        <LeagueStandingsMatrix
          :leagueId="activeLeague.id"
          :prefetchedData="standingsMap[activeLeague.id]"
          :level="activeLeague.level"
        />
      </div>
    </div>

    <q-separator v-if="activeLeagueView === 'all'" class="q-my-md" />

    <!-- Picks & Bans View -->
    <div
      v-if="activeLeagueView === 'picks' || activeLeagueView === 'all'"
      class="league-section"
    >
      <div
        v-if="activeLeagueView === 'all'"
        class="row items-center q-gutter-x-sm q-py-xs"
        :class="isMobile ? 'q-px-md' : 'q-px-xs'"
      >
        <q-icon name="casino" color="amber-9" size="20px" />
        <span class="text-subtitle1 text-weight-bold text-dark"
          >Picks &amp; Bans</span
        >
      </div>
      <div :class="isMobile ? 'q-px-none' : 'q-px-xs'">
        <PlayerCard
          v-if="activeLeagueMembers.length > 0"
          :all-members="activeLeagueMembers"
        />
        <div v-else class="q-pa-lg text-grey-6 italic text-center">
          No participant picks recorded for this league.
        </div>
      </div>
    </div>

    <q-separator v-if="activeLeagueView === 'all'" class="q-my-md" />

    <!-- Match Results View -->
    <div
      v-if="activeLeagueView === 'results' || activeLeagueView === 'all'"
      class="league-section"
    >
      <div
        v-if="activeLeagueView === 'all'"
        class="row items-center q-gutter-x-sm q-py-xs"
        :class="isMobile ? 'q-px-md' : 'q-px-xs'"
      >
        <q-icon name="scoreboard" color="indigo-7" size="20px" />
        <span class="text-subtitle1 text-weight-bold text-dark"
          >Match Results</span
        >
      </div>
      <div :class="isMobile ? 'q-px-none' : 'q-px-xs'">
        <LeagueMatchResults
          :leagueId="activeLeague.id"
          :show-standings="false"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import LeagueLevel from 'components/season/LeagueLevel.vue';
import UserAvatar from 'components/ui/UserAvatar.vue';
import LeagueStandingsMatrix from 'components/league/LeagueStandingsMatrix.vue';
import PlayerCard from 'components/league/PlayerCard.vue';
import LeagueMatchResults from 'components/league/LeagueMatchResults.vue';
import type {
  TLeagueDto,
  TSeasonParticipantDto,
  TSeasonLeagueStandings,
} from 'src/types';

defineProps<{
  activeLeague: TLeagueDto;
  activeLeagueMembers: TSeasonParticipantDto[];
  activeLeagueView: string;
  standingsMap: Record<number, TSeasonLeagueStandings>;
  isMobile: boolean;
  isUserInLeague: (id: number) => boolean;
  leagueDisplayName: (l: TLeagueDto) => string;
  leagueStatusColor: (status: string) => string;
  getMemberShape: (
    leagueId: number,
    profileId?: number,
    username?: string
  ) => string | undefined;
  getMemberColor: (
    leagueId: number,
    profileId?: number,
    username?: string
  ) => string | undefined;
}>();
</script>

<style scoped lang="scss">
.border-bottom-subtle {
  border-bottom: 1px solid var(--kenner-border-color);
}

.user-league-pill {
  font-size: 11px;
  font-weight: 700;
  color: var(--q-primary);
  background: rgba(var(--q-primary), 0.12);
  padding: 2px 8px;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
</style>

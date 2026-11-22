<template>
  <div class="column">
    <!-- Standings Matrix for All Leagues -->
    <template v-if="activeAllView === 'standings'">
      <div
        v-for="(league, index) in sortedLeagues"
        :key="league.id"
        class="league-standings-section"
        :class="{ 'league-section--user': isUserInLeague(league.id) }"
      >
        <q-separator v-if="index > 0" class="q-my-lg" />
        <div
          class="row items-center justify-between q-py-sm"
          :class="isMobile ? 'q-px-md' : 'q-px-xs'"
        >
          <div class="row items-center q-gutter-x-sm ellipsis col">
            <LeagueLevel :level="league.level" badge />
            <span class="text-subtitle1 text-weight-bold text-dark ellipsis">
              {{ leagueDisplayName(league) }} Standings Matrix
            </span>
            <div
              v-if="isUserInLeague(league.id)"
              class="user-league-pill row items-center no-wrap shrink-0"
            >
              <q-icon name="person" size="13px" class="q-mr-xs" />
              <span>Your League</span>
            </div>
          </div>
          <KennerButton
            flat
            dense
            no-caps
            color="primary"
            icon-right="chevron_right"
            label="Focus League"
            class="shrink-0"
            @click="$emit('selectLeague', league.id)"
          />
        </div>
        <div :class="isMobile ? 'q-px-none' : 'q-px-xs'">
          <LeagueStandingsMatrix
            :leagueId="league.id"
            :prefetchedData="standingsMap[league.id]"
            :level="league.level"
          />
        </div>
      </div>
    </template>

    <!-- Picks & Bans for All Leagues -->
    <template v-else-if="activeAllView === 'picks'">
      <div
        v-for="(league, index) in sortedLeagues"
        :key="league.id"
        class="league-picks-section"
        :class="{ 'league-section--user': isUserInLeague(league.id) }"
      >
        <q-separator v-if="index > 0" class="q-my-lg" />
        <div
          class="row items-center justify-between q-py-sm"
          :class="isMobile ? 'q-px-md' : 'q-px-xs'"
        >
          <div class="row items-center q-gutter-x-sm ellipsis col">
            <LeagueLevel :level="league.level" badge />
            <span class="text-subtitle1 text-weight-bold text-dark ellipsis">
              {{ leagueDisplayName(league) }} Picks &amp; Bans
            </span>
            <div
              v-if="isUserInLeague(league.id)"
              class="user-league-pill row items-center no-wrap shrink-0"
            >
              <q-icon name="person" size="13px" class="q-mr-xs" />
              <span>Your League</span>
            </div>
          </div>
          <KennerButton
            flat
            dense
            no-caps
            color="primary"
            icon-right="chevron_right"
            label="Focus League"
            class="shrink-0"
            @click="$emit('selectLeague', league.id)"
          />
        </div>
        <div :class="isMobile ? 'q-px-none' : 'q-px-xs'">
          <PlayerCard
            v-if="getMembersForLeague(league.id).length > 0"
            :all-members="getMembersForLeague(league.id)"
          />
          <div v-else class="q-pa-md text-grey-6 italic text-center">
            No participant picks recorded for this league.
          </div>
        </div>
      </div>
    </template>

    <!-- Match Results for All Leagues -->
    <template v-else-if="activeAllView === 'results'">
      <div
        v-for="(league, index) in sortedLeagues"
        :key="league.id"
        class="league-results-section"
        :class="{ 'league-section--user': isUserInLeague(league.id) }"
      >
        <q-separator v-if="index > 0" class="q-my-lg" />
        <div
          class="row items-center justify-between q-py-sm"
          :class="isMobile ? 'q-px-md' : 'q-px-xs'"
        >
          <div class="row items-center q-gutter-x-sm ellipsis col">
            <LeagueLevel :level="league.level" badge />
            <span class="text-subtitle1 text-weight-bold text-dark ellipsis">
              {{ leagueDisplayName(league) }} Match Results
            </span>
            <div
              v-if="isUserInLeague(league.id)"
              class="user-league-pill row items-center no-wrap shrink-0"
            >
              <q-icon name="person" size="13px" class="q-mr-xs" />
              <span>Your League</span>
            </div>
          </div>
          <KennerButton
            flat
            dense
            no-caps
            color="primary"
            icon-right="chevron_right"
            label="Focus League"
            class="shrink-0"
            @click="$emit('selectLeague', league.id)"
          />
        </div>
        <div :class="isMobile ? 'q-px-none' : 'q-px-xs'">
          <LeagueMatchResults :leagueId="league.id" :show-standings="false" />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import LeagueLevel from 'components/season/LeagueLevel.vue';
import KennerButton from 'components/base/KennerButton.vue';
import LeagueStandingsMatrix from 'components/league/LeagueStandingsMatrix.vue';
import PlayerCard from 'components/league/PlayerCard.vue';
import LeagueMatchResults from 'components/league/LeagueMatchResults.vue';
import type {
  TLeagueDto,
  TSeasonLeagueStandings,
  TSeasonParticipantDto,
} from 'src/types';

defineProps<{
  activeAllView: 'standings' | 'picks' | 'results';
  sortedLeagues: TLeagueDto[];
  standingsMap: Record<number, TSeasonLeagueStandings>;
  isMobile: boolean;
  isUserInLeague: (leagueId: number) => boolean;
  leagueDisplayName: (league: TLeagueDto) => string;
  getMembersForLeague: (leagueId: number) => TSeasonParticipantDto[];
}>();

defineEmits<{
  (e: 'selectLeague', leagueId: number): void;
}>();
</script>

<style scoped>
.shrink-0 {
  flex-shrink: 0;
}
.user-league-pill {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 10px;
  background: rgba(var(--q-primary-rgb, 25, 118, 210), 0.12);
  color: var(--q-primary);
}
.league-section--user {
  position: relative;
}
</style>

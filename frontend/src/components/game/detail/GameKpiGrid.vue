<template>
  <div>
    <!-- KPI Summary Cards Grid -->
    <div class="row q-col-gutter-md">
      <!-- High Score Card -->
      <div class="col-12 col-sm-6 col-lg-3">
        <OverviewCard
          title="High Score"
          icon="local_fire_department"
          icon-color="deep-orange"
        >
          <div v-if="stats.records.high_score" class="column q-gutter-y-xs">
            <div class="row items-baseline no-wrap">
              <span class="text-h4 text-weight-bolder text-deep-orange-9">
                {{ stats.records.high_score.points }}
              </span>
              <span class="text-caption text-grey-6 q-ml-xs">pts</span>
            </div>
            <div class="text-subtitle2 text-weight-bold ellipsis text-dark">
              {{ stats.records.high_score.profile_name }}
            </div>
            <div class="text-caption text-grey-6 ellipsis">
              {{ stats.records.high_score.season_name }} &middot;
              {{ stats.records.high_score.league_name }}
            </div>
            <KennerButton
              v-if="stats.records.high_score.match_id"
              flat
              dense
              no-caps
              size="sm"
              color="primary"
              icon-right="arrow_forward"
              label="View Match"
              class="q-mt-xs self-start"
              @click="$emit('viewMatch', stats.records.high_score.match_id)"
            />
          </div>
          <div v-else class="text-caption text-grey-6 q-py-sm">
            {{
              stats.game.has_points
                ? 'No recorded score yet'
                : 'Score-free game'
            }}
          </div>
        </OverviewCard>
      </div>

      <!-- Best Player / Win Rate Master -->
      <div class="col-12 col-sm-6 col-lg-3">
        <OverviewCard
          title="Top Performer"
          icon="emoji_events"
          icon-color="amber-8"
        >
          <div v-if="topPlayer" class="column q-gutter-y-xs">
            <div class="row items-baseline no-wrap">
              <span class="text-h4 text-weight-bolder text-amber-9">
                {{ topPlayer.win_rate }}%
              </span>
              <span class="text-caption text-grey-6 q-ml-xs">win rate</span>
            </div>
            <div class="text-subtitle2 text-weight-bold ellipsis text-dark">
              {{ topPlayer.profile_name }}
            </div>
            <div class="text-caption text-grey-6">
              {{ topPlayer.wins }} wins in {{ topPlayer.games_played }} plays
            </div>
          </div>
          <div v-else class="text-caption text-grey-6 q-py-sm">
            No ranked matches yet
          </div>
        </OverviewCard>
      </div>

      <!-- Activity Overview -->
      <div class="col-12 col-sm-6 col-lg-3">
        <OverviewCard
          title="Matches & Players"
          icon="sports_esports"
          icon-color="primary"
        >
          <div class="column q-gutter-y-xs">
            <div class="row items-baseline no-wrap">
              <span class="text-h4 text-weight-bolder text-primary">
                {{ stats.overview.total_matches }}
              </span>
              <span class="text-caption text-grey-6 q-ml-xs"
                >matches played</span
              >
            </div>
            <div class="text-body2 text-weight-medium text-grey-8">
              {{ stats.overview.distinct_players }} distinct players
            </div>
            <div class="text-caption text-grey-6">
              Across {{ stats.overview.distinct_seasons }} season(s)
            </div>
          </div>
        </OverviewCard>
      </div>

      <!-- Picks & Bans Popularity -->
      <div class="col-12 col-sm-6 col-lg-3">
        <OverviewCard
          title="Picks & Bans"
          icon="how_to_vote"
          icon-color="secondary"
        >
          <div class="column q-gutter-y-xs">
            <div class="row items-center justify-between">
              <span class="text-caption text-weight-bold text-grey-7"
                >Picks:</span
              >
              <span class="text-weight-bold text-positive">
                {{ stats.overview.total_picks }} &times;
              </span>
            </div>
            <div
              v-if="
                stats.superlatives.most_picked_by &&
                stats.superlatives.most_picked_by.length > 0
              "
              class="text-caption text-grey-7 ellipsis"
            >
              Top picker:
              <b>{{ stats.superlatives.most_picked_by[0].profile_name }}</b> ({{
                stats.superlatives.most_picked_by[0].count
              }})
            </div>

            <div class="row items-center justify-between q-mt-xs">
              <span class="text-caption text-weight-bold text-grey-7"
                >Bans:</span
              >
              <span class="text-weight-bold text-negative">
                {{ stats.overview.total_bans }} &times;
              </span>
            </div>
            <div
              v-if="
                stats.superlatives.most_banned_by &&
                stats.superlatives.most_banned_by.length > 0
              "
              class="text-caption text-grey-7 ellipsis"
            >
              Top banner:
              <b>{{ stats.superlatives.most_banned_by[0].profile_name }}</b> ({{
                stats.superlatives.most_banned_by[0].count
              }})
            </div>
          </div>
        </OverviewCard>
      </div>
    </div>

    <!-- Additional Scoring Stats if Points-Based Game -->
    <div
      v-if="stats.game.has_points && stats.records.avg_score !== null"
      class="row q-col-gutter-md q-mt-xs"
    >
      <div class="col-12">
        <q-card flat class="stat-banner-card">
          <q-card-section
            class="q-py-sm q-px-md row items-center justify-around text-center"
          >
            <div class="q-pa-xs">
              <div class="text-caption text-grey-6">Average Winning Score</div>
              <div class="text-subtitle1 text-weight-bold text-primary">
                {{ stats.records.avg_winning_score ?? '-' }} pts
              </div>
            </div>
            <q-separator vertical inset />
            <div class="q-pa-xs">
              <div class="text-caption text-grey-6">Average Overall Score</div>
              <div class="text-subtitle1 text-weight-bold text-grey-8">
                {{ stats.records.avg_score ?? '-' }} pts
              </div>
            </div>
            <q-separator vertical inset />
            <div class="q-pa-xs">
              <div class="text-caption text-grey-6">Lowest Recorded Score</div>
              <div class="text-subtitle1 text-weight-bold text-grey-8">
                {{ stats.records.low_score ?? '-' }} pts
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import OverviewCard from 'components/cards/OverviewCard.vue';
import KennerButton from 'components/base/KennerButton.vue';
import type {
  TGameDetailedStatistics,
  TGameLeaderboardPlayer,
} from 'src/types';

defineProps<{
  stats: TGameDetailedStatistics;
  topPlayer: TGameLeaderboardPlayer | null;
}>();

defineEmits<{
  (e: 'viewMatch', matchId: number): void;
}>();
</script>

<style scoped>
.stat-banner-card {
  border-radius: 12px;
  background: var(--kenner-surface-subtle);
  border: 1px solid var(--kenner-border-subtle);
}
</style>

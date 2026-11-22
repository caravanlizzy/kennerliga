<template>
  <q-page class="q-pa-md max-width-container q-mx-auto game-detail-page">
    <div v-if="loading" class="q-py-xl text-center">
      <LoadingSpinner />
    </div>

    <div v-else-if="error || !stats" class="q-py-md">
      <q-banner rounded dense class="bg-red-1 text-negative q-mb-md">
        <template #avatar><q-icon name="warning" color="negative" /></template>
        {{ error || 'Game details could not be loaded.' }}
      </q-banner>
      <KennerButton
        outline
        no-caps
        icon="arrow_back"
        label="Back to Statistics"
        @click="router.push({ name: 'statistics' })"
      />
    </div>

    <div v-else class="column q-gutter-y-lg">
      <!-- Header & Hero Section -->
      <q-card flat class="game-hero-card">
        <q-card-section class="q-pa-lg">
          <div class="row items-start justify-between q-col-gutter-md">
            <div>
              <!-- Badges Row -->
              <div class="row items-center q-gutter-x-sm q-gutter-y-xs q-mb-sm">
                <q-btn
                  flat
                  dense
                  no-caps
                  size="sm"
                  color="grey-7"
                  icon="arrow_back"
                  label="Statistics"
                  class="q-mr-xs"
                  @click="router.push({ name: 'statistics' })"
                />
                <q-badge color="primary" text-color="white" class="q-px-sm text-weight-bold">
                  {{ stats.game.platform.name || 'Board Game' }}
                </q-badge>
                <q-badge color="secondary" text-color="white" class="q-px-sm">
                  {{ stats.game.min_players }} - {{ stats.game.max_players }} Players
                </q-badge>
                <q-badge
                  v-if="stats.game.is_asymmetric"
                  color="purple-1"
                  text-color="purple-9"
                  class="q-px-sm text-weight-medium"
                >
                  <q-icon name="shield" size="12px" class="q-mr-xs" />
                  Asymmetric Factions
                </q-badge>
                <q-badge
                  v-if="!(stats.game.selectable ?? true)"
                  color="red-1"
                  text-color="negative"
                  class="q-px-sm text-weight-bold"
                >
                  <q-icon name="block" size="12px" class="q-mr-xs" />
                  Not Selectable
                </q-badge>
              </div>

              <!-- Title -->
              <h1 class="text-h4 text-weight-bolder text-grey-9 q-my-none">
                {{ stats.game.name }}
              </h1>
              <div
                v-if="stats.game.short_name && stats.game.short_name !== stats.game.name"
                class="text-subtitle2 text-grey-6 q-mt-xs"
              >
                ({{ stats.game.short_name }})
              </div>
            </div>

            <!-- Action Buttons for Admins -->
            <div class="row items-center q-gutter-sm">
              <KennerButton
                v-if="isAdmin"
                outline
                no-caps
                size="sm"
                color="secondary"
                icon="settings"
                label="View Configuration"
                @click="
                  router.push({
                    name: 'game-config',
                    params: { id: stats.game.id },
                  })
                "
              />
              <KennerButton
                v-if="isAdmin"
                outline
                no-caps
                size="sm"
                color="primary"
                icon="edit"
                label="Edit Game"
                @click="
                  router.push({
                    name: 'game-edit',
                    params: { id: stats.game.id },
                  })
                "
              />
            </div>
          </div>

          <!-- Filter Toolbar within Game Details -->
          <q-separator class="q-my-md" />

          <div class="row items-center justify-between q-col-gutter-sm">
            <!-- Player Count Chips -->
            <div class="col-12 col-sm-auto">
              <div class="filter-box row items-center q-gutter-x-xs q-px-sm q-py-xs">
                <q-icon name="groups" size="18px" class="q-mr-xs text-primary" />
                <span class="text-caption text-weight-bold text-grey-8 q-mr-xs">Player Count:</span>
                <q-chip
                  clickable
                  dense
                  :outline="!isAllPlayerCountsSelected"
                  :color="isAllPlayerCountsSelected ? 'primary' : 'grey-7'"
                  text-color="white"
                  size="sm"
                  class="text-weight-bold"
                  style="border-radius: 4px"
                  @click="toggleAllPlayerCounts"
                >
                  All
                </q-chip>
                <q-chip
                  v-for="pc in availablePlayerCounts"
                  :key="pc"
                  clickable
                  dense
                  :outline="!selectedPlayerCounts.includes(pc)"
                  :color="
                    selectedPlayerCounts.includes(pc) ? 'primary' : 'grey-7'
                  "
                  text-color="white"
                  size="sm"
                  class="text-weight-bold"
                  style="border-radius: 4px"
                  @click="togglePlayerCount(pc)"
                >
                  {{ pc.toUpperCase() }}
                </q-chip>
              </div>
            </div>

            <!-- Years Filter -->
            <div class="col-12 col-sm-auto years-filter" style="min-width: 170px">
              <KennerSelect
                v-model="selectedYears"
                :options="yearOptions"
                label="Years"
                multiple
                clearable
                dense
                :display-value="yearsDisplayValue"
              />
            </div>
          </div>
        </q-card-section>
      </q-card>

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
                @click="
                  router.push({
                    name: 'match-result-detail',
                    params: { id: stats.records.high_score.match_id },
                  })
                "
              />
            </div>
            <div v-else class="text-caption text-grey-6 q-py-sm">
              {{ stats.game.has_points ? 'No recorded score yet' : 'Score-free game' }}
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
                <span class="text-caption text-grey-6 q-ml-xs">matches played</span>
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
                <span class="text-caption text-weight-bold text-grey-7">Picks:</span>
                <span class="text-weight-bold text-positive">
                  {{ stats.overview.total_picks }} &times;
                </span>
              </div>
              <div
                v-if="stats.superlatives.most_picked_by && stats.superlatives.most_picked_by.length > 0"
                class="text-caption text-grey-7 ellipsis"
              >
                Top picker: <b>{{ stats.superlatives.most_picked_by[0].profile_name }}</b> ({{ stats.superlatives.most_picked_by[0].count }})
              </div>

              <div class="row items-center justify-between q-mt-xs">
                <span class="text-caption text-weight-bold text-grey-7">Bans:</span>
                <span class="text-weight-bold text-negative">
                  {{ stats.overview.total_bans }} &times;
                </span>
              </div>
              <div
                v-if="stats.superlatives.most_banned_by && stats.superlatives.most_banned_by.length > 0"
                class="text-caption text-grey-7 ellipsis"
              >
                Top banner: <b>{{ stats.superlatives.most_banned_by[0].profile_name }}</b> ({{ stats.superlatives.most_banned_by[0].count }})
              </div>
            </div>
          </OverviewCard>
        </div>
      </div>

      <!-- Additional Scoring Stats if Points-Based Game -->
      <div
        v-if="stats.game.has_points && stats.records.avg_score !== null"
        class="row q-col-gutter-md"
      >
        <div class="col-12">
          <q-card flat class="stat-banner-card">
            <q-card-section class="q-py-sm q-px-md row items-center justify-around text-center">
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

      <!-- Main Tabs for Deep Dive -->
      <div>
        <q-tabs
          v-model="activeTab"
          dense
          class="text-grey-7 stats-tabs q-mb-md"
          active-color="primary"
          indicator-color="primary"
          align="left"
          narrow-indicator
        >
          <q-tab name="leaderboard" icon="leaderboard" label="Player Leaderboard" />
          <q-tab
            name="matches"
            icon="history"
            :label="`Match History (${stats.recent_matches.length})`"
          />
          <q-tab
            v-if="hasFactionsOrRules"
            name="factions"
            icon="shield"
            label="Factions & Game Rules"
          />
        </q-tabs>

        <q-tab-panels
          v-model="activeTab"
          animated
          class="bg-transparent"
        >
          <!-- TAB 1: Leaderboard -->
          <q-tab-panel name="leaderboard" class="q-pa-none">
            <q-card flat bordered class="rounded-borders bg-white overflow-hidden">
              <q-card-section class="q-pa-md border-bottom bg-grey-1">
                <div class="row items-center justify-between">
                  <div class="text-subtitle1 text-weight-bold text-dark">
                    Player Performance Rankings
                  </div>
                  <div class="text-caption text-grey-6">
                    Ranked by Win Rate &middot; Ties broken by Average Position
                  </div>
                </div>
              </q-card-section>

              <KennerTable
                v-if="stats.leaderboard && stats.leaderboard.length > 0"
                flat
                :rows="stats.leaderboard"
                :columns="leaderboardColumns"
                row-key="profile_id"
              >
                <!-- Rank slot -->
                <template v-slot:body-cell-rank="props">
                  <q-td :props="props">
                    <span
                      v-if="props.row.rank && props.row.rank <= 3"
                      class="rank-badge"
                      :class="`rank-badge--${props.row.rank - 1}`"
                    >
                      {{ props.row.rank }}
                    </span>
                    <span
                      v-else-if="props.row.rank"
                      class="text-weight-bold text-grey-7"
                    >
                      #{{ props.row.rank }}
                    </span>
                    <span v-else class="text-caption text-grey-5">-</span>
                  </q-td>
                </template>

                <!-- Player Name slot -->
                <template v-slot:body-cell-profile_name="props">
                  <q-td :props="props">
                    <div class="row items-center no-wrap">
                      <span
                        class="text-weight-bold"
                        :class="props.row.is_me ? 'text-primary' : 'text-grey-9'"
                      >
                        {{ props.row.profile_name }}
                      </span>
                      <q-badge
                        v-if="props.row.is_me"
                        color="primary"
                        text-color="white"
                        class="q-ml-xs text-weight-bold"
                        label="YOU"
                      />
                    </div>
                  </q-td>
                </template>

                <!-- Win Rate slot -->
                <template v-slot:body-cell-win_rate="props">
                  <q-td :props="props">
                    <div class="row items-center no-wrap">
                      <span
                        class="text-weight-bolder"
                        :class="props.row.win_rate >= 50 ? 'text-positive' : 'text-grey-8'"
                      >
                        {{ props.row.win_rate }}%
                      </span>
                    </div>
                  </q-td>
                </template>
              </KennerTable>

              <div v-else class="text-center q-py-xl text-grey-6">
                <q-icon name="sports_esports" size="40px" class="q-mb-sm text-grey-4" />
                <div class="text-subtitle2">No match results recorded yet</div>
                <div class="text-caption">
                  Results will appear here as soon as matches for this game are finished.
                </div>
              </div>
            </q-card>
          </q-tab-panel>

          <!-- TAB 2: Match History -->
          <q-tab-panel name="matches" class="q-pa-none">
            <div v-if="stats.recent_matches.length > 0" class="column q-gutter-y-md">
              <q-card
                v-for="match in stats.recent_matches"
                :key="match.id"
                flat
                bordered
                class="match-history-card rounded-borders bg-white"
              >
                <!-- Match Header -->
                <q-card-section class="q-py-sm q-px-md bg-grey-1 border-bottom">
                  <div class="row items-center justify-between no-wrap">
                    <div class="row items-center q-gutter-x-sm">
                      <q-badge color="primary" text-color="white">
                        {{ match.season_name || `Season #${match.season_id}` }}
                      </q-badge>
                      <q-badge color="secondary" text-color="white">
                        {{ match.league_name || (match.league_level != null ? `League ${match.league_level}` : 'League') }}
                      </q-badge>
                      <span class="text-caption text-grey-6">
                        {{ formatDate(match.date) }}
                      </span>
                    </div>

                    <KennerButton
                      flat
                      dense
                      no-caps
                      size="sm"
                      color="primary"
                      icon-right="arrow_forward"
                      label="Match Details"
                      @click="
                        router.push({
                          name: 'match-result-detail',
                          params: { id: match.id },
                        })
                      "
                    />
                  </div>
                </q-card-section>

                <!-- Match Results Participants -->
                <q-card-section class="q-pa-md">
                  <div class="row q-col-gutter-sm">
                    <div
                      v-for="part in match.participants"
                      :key="part.profile_id"
                      class="col-12 col-sm-6 col-md-4"
                    >
                      <div
                        class="participant-item q-pa-sm rounded-borders row items-center justify-between no-wrap"
                        :class="{
                          'participant-item--winner': part.is_winner,
                          'bg-grey-1': !part.is_winner,
                        }"
                      >
                        <div class="row items-center no-wrap ellipsis">
                          <span
                            class="rank-badge q-mr-sm"
                            :class="`rank-badge--${(part.position || 1) - 1}`"
                          >
                            {{ part.position }}
                          </span>
                          <div class="ellipsis">
                            <div class="text-weight-bold text-body2 ellipsis">
                              {{ part.profile_name }}
                            </div>
                            <div
                              v-if="part.faction_name || part.win_condition_name"
                              class="text-caption text-grey-6 ellipsis"
                            >
                              {{ part.faction_name || part.win_condition_name }}
                            </div>
                          </div>
                        </div>

                        <div v-if="part.points !== null" class="text-weight-bolder text-right">
                          <span
                            :class="part.is_winner ? 'text-deep-orange-9' : 'text-grey-8'"
                          >
                            {{ part.points }}
                          </span>
                          <span class="text-caption text-grey-6 q-ml-xs">pts</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Selected Options Chips (if any) -->
                  <div
                    v-if="match.selected_options && match.selected_options.length > 0"
                    class="row items-center q-gutter-xs q-mt-sm"
                  >
                    <span class="text-caption text-grey-6 q-mr-xs">Rules:</span>
                    <q-chip
                      v-for="(opt, oIdx) in match.selected_options"
                      :key="oIdx"
                      dense
                      size="sm"
                      color="grey-2"
                      text-color="grey-8"
                    >
                      <span class="text-weight-bold q-mr-xs">{{ opt.option_name }}:</span>
                      <span>{{ opt.choice_name }}</span>
                    </q-chip>
                  </div>
                </q-card-section>
              </q-card>
            </div>

            <div v-else class="text-center q-py-xl text-grey-6 bg-white rounded-borders">
              <q-icon name="history" size="40px" class="q-mb-sm text-grey-4" />
              <div class="text-subtitle2">No matches played yet</div>
            </div>
          </q-tab-panel>

          <!-- TAB 3: Factions & Rules -->
          <q-tab-panel name="factions" class="q-pa-none">
            <div class="column q-gutter-y-lg">
              <!-- Faction Performance Table (if factions exist) -->
              <q-card
                v-if="stats.factions && stats.factions.length > 0"
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
                      {{ stats.factions.length }} configured factions
                    </div>
                  </div>
                </q-card-section>

                <KennerTable
                  flat
                  :rows="stats.factions"
                  :columns="factionColumns"
                  row-key="id"
                >
                  <template v-slot:body-cell-win_rate="props">
                    <q-td :props="props">
                      <span
                        class="text-weight-bold"
                        :class="props.row.win_rate >= 50 ? 'text-positive' : 'text-grey-8'"
                      >
                        {{ props.row.win_rate }}%
                      </span>
                    </q-td>
                  </template>
                </KennerTable>
              </q-card>

              <!-- Game Configuration Summary Card -->
              <q-card flat bordered class="rounded-borders bg-white">
                <q-card-section class="q-pa-md border-bottom bg-grey-1 row items-center justify-between">
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
                    @click="
                      router.push({
                        name: 'game-config',
                        params: { id: stats.game.id },
                      })
                    "
                  />
                </q-card-section>

                <q-card-section class="q-pa-md">
                  <div class="row q-col-gutter-md">
                    <div class="col-12 col-md-6">
                      <div class="text-caption text-weight-bold text-grey-7 text-uppercase q-mb-xs">
                        Scoring &amp; Mechanics
                      </div>
                      <q-list dense separator class="rounded-borders border-light bg-grey-1">
                        <q-item>
                          <q-item-section>Points-based Scoring</q-item-section>
                          <q-item-section side>
                            <q-badge :color="stats.game.has_points ? 'positive' : 'grey-6'">
                              {{ stats.game.has_points ? 'Yes' : 'No' }}
                            </q-badge>
                          </q-item-section>
                        </q-item>
                        <q-item>
                          <q-item-section>Asymmetric Factions</q-item-section>
                          <q-item-section side>
                            <q-badge :color="stats.game.is_asymmetric ? 'purple' : 'grey-6'">
                              {{ stats.game.is_asymmetric ? 'Yes' : 'No' }}
                            </q-badge>
                          </q-item-section>
                        </q-item>
                        <q-item>
                          <q-item-section>Starting Player Order</q-item-section>
                          <q-item-section side>
                            <q-badge :color="stats.game.has_starting_player_order ? 'positive' : 'grey-6'">
                              {{ stats.game.has_starting_player_order ? 'Yes' : 'No' }}
                            </q-badge>
                          </q-item-section>
                        </q-item>
                        <q-item v-if="stats.game.starting_points_system">
                          <q-item-section>Starting Points System</q-item-section>
                          <q-item-section side class="text-weight-medium text-dark">
                            {{ stats.game.starting_points_system }}
                          </q-item-section>
                        </q-item>
                      </q-list>
                    </div>

                    <div class="col-12 col-md-6">
                      <div class="text-caption text-weight-bold text-grey-7 text-uppercase q-mb-xs">
                        Configured Options &amp; Variants
                      </div>
                      <div v-if="stats.game.options && stats.game.options.length > 0">
                        <div
                          v-for="opt in stats.game.options"
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
                      <div v-else class="text-caption text-grey-6 q-pa-sm">
                        No special variant options configured.
                      </div>
                    </div>
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </q-tab-panel>
        </q-tab-panels>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from 'src/stores/userStore';
import { fetchGameDetailedStatistics } from 'src/services/statisticsService';
import {
  TGameDetailedStatistics,
  TGameFactionStat,
  TGameLeaderboardPlayer,
} from 'src/types';
import OverviewCard from 'components/cards/OverviewCard.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTable from 'components/tables/KennerTable.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const isAdmin = computed(() => userStore.isAdmin);

const loading = ref(true);
const error = ref<string | null>(null);
const stats = ref<TGameDetailedStatistics | null>(null);

const activeTab = ref<'leaderboard' | 'matches' | 'factions'>('leaderboard');

// Filters
const selectedYears = ref<number[]>([]);
const selectedPlayerCounts = ref<string[]>([]);
const availablePlayerCounts = ['2p', '3p', '4p', '5p', '6p'];

const yearOptions = [
  { label: '2026', value: 2026 },
  { label: '2025', value: 2025 },
];

const isAllPlayerCountsSelected = computed(
  () => selectedPlayerCounts.value.length === 0
);

function toggleAllPlayerCounts() {
  selectedPlayerCounts.value = [];
}

function togglePlayerCount(count: string) {
  const index = selectedPlayerCounts.value.indexOf(count);
  if (index === -1) {
    selectedPlayerCounts.value.push(count);
  } else {
    selectedPlayerCounts.value.splice(index, 1);
  }
}

const yearsDisplayValue = computed(() => {
  if (selectedYears.value.length === 0) return 'All Years';
  return selectedYears.value.join(', ');
});

const topPlayer = computed<TGameLeaderboardPlayer | null>(() => {
  if (!stats.value?.leaderboard || stats.value.leaderboard.length === 0) {
    return null;
  }
  return stats.value.leaderboard[0];
});

const hasFactionsOrRules = computed(() => {
  return (
    (stats.value?.factions && stats.value.factions.length > 0) ||
    Boolean(stats.value?.game.options && stats.value.game.options.length > 0) ||
    Boolean(stats.value?.game.is_asymmetric)
  );
});

async function loadData() {
  const gameId = Number(route.params.id);
  if (!gameId || isNaN(gameId)) {
    error.value = 'Invalid game id';
    loading.value = false;
    return;
  }
  try {
    loading.value = true;
    error.value = null;
    const data = await fetchGameDetailedStatistics(
      gameId,
      selectedYears.value,
      selectedPlayerCounts.value,
      0
    );
    if (!data) {
      error.value = 'Game not found';
    } else {
      stats.value = data;
    }
  } catch (e: any) {
    error.value = e?.message || 'Could not load game statistics';
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadData();
});

watch(
  [selectedYears, selectedPlayerCounts],
  () => {
    loadData();
  },
  { deep: true }
);

watch(
  () => route.params.id,
  (newId) => {
    if (newId) loadData();
  }
);

function formatDate(dateStr?: string) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

// Columns definition for Leaderboard
const leaderboardColumns = [
  {
    name: 'rank',
    label: 'Rank',
    field: (r: TGameLeaderboardPlayer) => r.rank,
    align: 'center',
    sortable: true,
  },
  {
    name: 'profile_name',
    label: 'Player',
    field: (r: TGameLeaderboardPlayer) => r.profile_name,
    align: 'left',
    sortable: true,
  },
  {
    name: 'win_rate',
    label: 'Win Rate',
    field: (r: TGameLeaderboardPlayer) => r.win_rate,
    align: 'left',
    sortable: true,
  },
  {
    name: 'games_played',
    label: 'Matches',
    field: (r: TGameLeaderboardPlayer) => `${r.wins} / ${r.games_played}`,
    align: 'center',
    sortable: true,
  },
  {
    name: 'avg_position',
    label: 'Avg Position',
    field: (r: TGameLeaderboardPlayer) =>
      r.avg_position !== null ? r.avg_position : '-',
    align: 'center',
    sortable: true,
  },
  {
    name: 'best_score',
    label: 'Best Score',
    field: (r: TGameLeaderboardPlayer) =>
      r.best_score !== null ? r.best_score : '-',
    align: 'center',
    sortable: true,
  },
  {
    name: 'avg_score',
    label: 'Avg Score',
    field: (r: TGameLeaderboardPlayer) =>
      r.avg_score !== null ? r.avg_score : '-',
    align: 'center',
    sortable: true,
  },
];

// Columns definition for Factions
const factionColumns = [
  {
    name: 'name',
    label: 'Faction',
    field: (r: TGameFactionStat) => r.name,
    align: 'left',
    sortable: true,
  },
  {
    name: 'games_played',
    label: 'Plays',
    field: (r: TGameFactionStat) => r.games_played,
    align: 'center',
    sortable: true,
  },
  {
    name: 'wins',
    label: 'Wins',
    field: (r: TGameFactionStat) => r.wins,
    align: 'center',
    sortable: true,
  },
  {
    name: 'win_rate',
    label: 'Win Rate',
    field: (r: TGameFactionStat) => r.win_rate,
    align: 'center',
    sortable: true,
  },
  {
    name: 'avg_position',
    label: 'Avg Position',
    field: (r: TGameFactionStat) => (r.avg_position !== null ? r.avg_position : '-'),
    align: 'center',
    sortable: true,
  },
  {
    name: 'avg_points',
    label: 'Avg Points',
    field: (r: TGameFactionStat) => (r.avg_points !== null ? r.avg_points : '-'),
    align: 'center',
    sortable: true,
  },
  {
    name: 'best_score',
    label: 'Best Score',
    field: (r: TGameFactionStat) => (r.best_score !== null ? r.best_score : '-'),
    align: 'center',
    sortable: true,
  },
];
</script>

<style scoped lang="scss">
.game-detail-page {
  max-width: 1200px;
}

.game-hero-card {
  background: var(--kenner-surface-overlay);
  backdrop-filter: blur(8px);
  border: 1px solid var(--kenner-border-color, rgba(0, 0, 0, 0.08));
  border-radius: var(--kenner-card-radius, 16px);
}

.stat-banner-card {
  background: var(--kenner-surface-overlay);
  border: 1px solid var(--kenner-border-color, rgba(0, 0, 0, 0.08));
  border-radius: 12px;
}

.match-history-card {
  border: 1px solid var(--kenner-border-color, rgba(0, 0, 0, 0.08));
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  &:hover {
    border-color: var(--kenner-border-color-hover, rgba(99, 102, 241, 0.3));
  }
}

.participant-item {
  border: 1px solid var(--kenner-border-subtle, rgba(0, 0, 0, 0.04));
  &--winner {
    background: rgba(245, 158, 11, 0.08);
    border-color: rgba(245, 158, 11, 0.3);
  }
}

.filter-box {
  background: var(--kenner-surface-overlay, #ffffff);
  border: 1px solid var(--kenner-border-color, rgba(0, 0, 0, 0.08));
  border-radius: 8px;
}

.border-light {
  border: 1px solid var(--kenner-border-subtle, rgba(0, 0, 0, 0.08));
}

.border-bottom {
  border-bottom: 1px solid var(--kenner-border-subtle, rgba(0, 0, 0, 0.08));
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.06);
  font-size: 11px;
  font-weight: 700;
  color: var(--kenner-text-muted);
  flex-shrink: 0;

  &--0 {
    background: #f6d365;
    color: #7a5b00;
  }
  &--1 {
    background: #d7dde8;
    color: #4b5563;
  }
  &--2 {
    background: #d6a77a;
    color: #6b3f16;
  }
}
</style>

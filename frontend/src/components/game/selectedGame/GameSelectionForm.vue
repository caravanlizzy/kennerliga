<template>
  <q-card flat class="modern-details-card">
    <q-inner-loading
      v-if="isLoading"
      :showing="isLoading"
      class="rounded-borders"
    >
      <q-spinner-puff size="4em" color="primary" />
    </q-inner-loading>

    <template v-else>
      <!-- Optional External Header Slot -->
      <div v-if="$slots.header" class="q-pa-md border-bottom-subtle">
        <slot name="header" />
      </div>

      <!-- Header -->
      <div class="q-pa-md">
        <div class="column q-mb-md">
          <!-- Platform info -->
          <div class="row items-center q-gutter-x-sm q-mb-xs">
            <q-badge
              rounded
              :color="
                getPlatformColor(
                  getPlatformName(platforms, gameInformation.game.platform)
                ).color
              "
              style="width: 10px; height: 10px; padding: 0"
            />
            <span
              class="text-overline text-grey-7 font-weight-700 letter-spacing-1"
            >
              {{
                getPlatformName(platforms, gameInformation.game.platform).split(
                  '.'
                )[0]
              }}
            </span>
          </div>

          <!-- Title and Button Row -->
          <div
            class="row items-center justify-between no-wrap"
            :class="isMobile ? 'q-gutter-x-sm' : 'q-gutter-x-lg'"
          >
            <div
              class="text-weight-bolder text-dark line-height-1 ellipsis"
              :class="isMobile ? 'text-subtitle1' : 'text-h6'"
            >
              {{ gameInformation.game.name }}
            </div>

            <div class="flex-shrink-0">
              <KennerButton
                :size="isMobile ? 'sm' : 'md'"
                :color="isValid ? 'primary' : 'grey-4'"
                icon="check_circle"
                :disable="!isValid"
                @click="onSubmit"
                class="shadow-premium save-btn"
              >
                {{ isMobile ? 'Confirm' : 'Confirm Selection' }}
              </KennerButton>
            </div>
          </div>
        </div>

        <q-separator class="q-mb-md opacity-10" />

        <!-- League Matchup Stats Section (on-demand after selecting game) -->
        <div v-if="leagueId" class="matchup-section q-mb-md">
          <div class="row items-center justify-between q-mb-xs">
            <div class="row items-center q-gutter-x-xs">
              <q-icon name="insights" size="18px" color="primary" />
              <div
                class="text-caption text-weight-bold text-uppercase letter-spacing-1 text-grey-8"
              >
                Matchup vs. this league
              </div>
              <q-icon
                name="info_outline"
                size="14px"
                color="grey-5"
                class="cursor-pointer"
              >
                <q-tooltip max-width="260px">
                  Estimated chance to finish ahead of current league members,
                  based on past performance and direct head-to-head matches.
                </q-tooltip>
              </q-icon>
            </div>

            <q-btn
              v-if="stats && stats.opponents && stats.opponents.length > 0"
              flat
              dense
              no-caps
              size="xs"
              color="grey-7"
              :icon-right="showOpponentBreakdown ? 'expand_less' : 'expand_more'"
              :label="showOpponentBreakdown ? 'Hide details' : 'Opponent breakdown'"
              @click="showOpponentBreakdown = !showOpponentBreakdown"
            />
          </div>

          <!-- Loading state -->
          <div
            v-if="isLoadingStats"
            class="q-pa-sm bg-blue-grey-1 rounded-borders border-subtle row items-center q-gutter-x-sm"
          >
            <q-spinner-dots size="18px" color="primary" />
            <span class="text-caption text-grey-7 font-weight-500">
              Calculating stats vs. league members…
            </span>
          </div>

          <!-- Loaded stats card -->
          <div
            v-else-if="stats"
            class="matchup-card bg-blue-grey-1 q-pa-sm rounded-borders border-subtle"
          >
            <div class="row items-center justify-between no-wrap q-gutter-x-sm">
              <div class="row items-center q-gutter-x-sm">
                <q-badge
                  :color="getWinChanceColor(stats.win_chance)"
                  class="text-weight-bolder q-px-sm q-py-xs text-body2"
                >
                  {{ Math.round(stats.win_chance) }}% Win Chance
                </q-badge>
                <div class="text-caption text-grey-8 font-weight-500">
                  <span v-if="stats.games_played > 0">
                    You: {{ stats.wins }} win{{ stats.wins === 1 ? '' : 's' }} in
                    {{ stats.games_played }} game{{
                      stats.games_played === 1 ? '' : 's'
                    }}
                  </span>
                  <span v-else class="text-grey-6">
                    You: First time playing
                  </span>
                </div>
              </div>

              <div
                v-if="stats.shared_matches > 0"
                class="text-caption text-grey-6 text-right flex-shrink-0"
              >
                {{ stats.shared_matches }} shared match{{
                  stats.shared_matches === 1 ? '' : 'es'
                }}
              </div>
            </div>

            <!-- Opponents breakdown -->
            <q-slide-transition>
              <div
                v-if="showOpponentBreakdown && stats.opponents && stats.opponents.length > 0"
                class="q-pt-sm q-mt-xs border-top-subtle"
              >
                <div class="row q-col-gutter-xs">
                  <div
                    v-for="opp in stats.opponents"
                    :key="opp.profile_id"
                    class="col-12 col-sm-6"
                  >
                    <div class="opponent-chip row items-center justify-between q-px-sm q-py-xs rounded-borders bg-white border-subtle">
                      <span class="ellipsis text-caption font-weight-600 text-dark">
                        {{ opp.profile_name || 'Opponent' }}
                      </span>
                      <div class="row items-center q-gutter-x-xs flex-shrink-0">
                        <span
                          class="text-caption text-weight-bold"
                          :class="getOpponentChanceClass(opp.chance)"
                        >
                          {{ Math.round(opp.chance) }}%
                        </span>
                        <q-tooltip>
                          <div><strong>{{ opp.profile_name || 'Opponent' }}</strong>: {{ Math.round(opp.chance) }}% estimated win chance</div>
                          <div v-if="opp.shared_matches > 0">
                            {{ opp.shared_matches }} direct head-to-head match{{ opp.shared_matches === 1 ? '' : 'es' }}
                          </div>
                          <div v-else-if="opp.opponent_games > 0">
                            {{ opp.opponent_games }} match{{ opp.opponent_games === 1 ? '' : 'es' }} played (0 direct)
                          </div>
                          <div v-else>
                            0 matches played
                          </div>
                        </q-tooltip>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </q-slide-transition>
          </div>
        </div>

        <!-- No settings (use conditional visibility) -->
        <div
          v-if="!visibleOptionsSafe.length"
          class="text-center q-pa-md bg-blue-grey-1 rounded-borders border-subtle"
        >
          <q-icon name="info" size="xs" color="grey-5" class="q-mb-xs" />
          <div class="text-caption text-grey-7 font-weight-500">
            No additional settings for this game.
          </div>
        </div>

        <!-- Settings -->
        <template v-else>
          <div class="row items-center q-gutter-x-sm q-mb-md">
            <q-icon name="settings" size="18px" class="text-selected" />
            <div
              class="text-subtitle2 text-weight-bold text-uppercase letter-spacing-1 text-selected"
            >
              Game Settings
            </div>
          </div>

          <!-- Choices -->
          <div
            v-if="visibleOptionsSafe.some((o) => o.has_choices)"
            class="q-mb-md"
          >
            <div class="row q-col-gutter-md">
              <div
                v-for="option in visibleOptionsSafe.filter(
                  (o) => o.has_choices
                )"
                :key="option.id"
                class="col-12 col-sm-6"
              >
                <KennerSelect
                  :options="option.choices || null"
                  :label="option.name"
                  option-label="name"
                  v-model="findSelectedOption(option.id).choice"
                  :rules="[(val) => !!val || `${option.name} is required`]"
                  class="full-width"
                />
              </div>
            </div>
          </div>

          <!-- Toggles -->
          <div
            v-if="visibleOptionsSafe.some((o) => !o.has_choices)"
            class="bg-blue-grey-1 q-pa-md rounded-borders border-subtle"
          >
            <div
              class="text-caption text-weight-bold text-grey-7 text-uppercase q-mb-sm letter-spacing-1"
            >
              Toggles
            </div>
            <div class="row q-col-gutter-sm">
              <div
                v-for="option in visibleOptionsSafe.filter(
                  (o) => !o.has_choices
                )"
                :key="option.id"
                class="col-auto"
              >
                <q-toggle
                  v-model="findSelectedOption(option.id).value"
                  :label="option.name"
                  dense
                  color="primary"
                  class="font-weight-600"
                />
              </div>
            </div>
          </div>
        </template>
      </div>
    </template>
  </q-card>
</template>

<style lang="scss" scoped>
.modern-details-card {
  border-radius: 24px;
  background: var(--kenner-card-bg);
  border: 1px solid var(--kenner-border-subtle);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
  position: relative;
  overflow: hidden;
}

.line-height-1 {
  line-height: 1.1;
}

.letter-spacing-1 {
  letter-spacing: 0.05em;
}

.save-btn {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  &:not(.q-btn--disabled) {
    animation: pulse-btn 2.5s infinite;
    background: linear-gradient(
      135deg,
      $kenner-red 0%,
      darken($kenner-red, 10%) 100%
    ) !important;
    color: white !important;
  }
}

.shadow-premium {
  box-shadow: 0 4px 14px 0 rgba($kenner-red, 0.39);
}

@keyframes pulse-btn {
  0% {
    box-shadow: 0 0 0 0 rgba($kenner-red, 0.5);
  }
  70% {
    box-shadow: 0 0 0 12px rgba($kenner-red, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba($kenner-red, 0);
  }
}

.text-selected {
  color: $kenner-red;
}

.font-weight-500 {
  font-weight: 500;
}

.font-weight-600 {
  font-weight: 600;
}

.flex-shrink-0 {
  flex-shrink: 0;
}

.opacity-10 {
  opacity: 0.1;
}

.border-subtle {
  border: 1px solid var(--kenner-border-subtle);
}

.border-bottom-subtle {
  border-bottom: 1px solid var(--kenner-border-subtle);
}

.border-top-subtle {
  border-top: 1px solid var(--kenner-border-subtle);
}

.opponent-chip {
  min-height: 32px;
}
</style>

<script setup lang="ts">
import KennerSelect from 'components/base/KennerSelect.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { useResponsive } from 'src/composables/responsive';
import {
  getPlatformColor,
  getPlatformName,
} from 'src/composables/gameSelection';
import { fetchGameWinStats } from 'src/services/statisticsService';
import {
  TPlatform,
  TGameInformation,
  TGameSelection,
  TGameOptionDto,
  TWinSuggestion,
} from 'src/types';
import { computed, inject, ref, watch } from 'vue';

const platforms = inject<TPlatform[]>('platforms', []);
const { isMobile } = useResponsive();

const props = withDefaults(
  defineProps<{
    gameInformation: TGameInformation;
    gameSelection: TGameSelection;
    isLoading: boolean;
    isValid: boolean;
    onSubmit: () => void;

    // comes from useGameSelection(...).visibleOptions
    visibleOptions?: TGameOptionDto[];
    leagueId?: number;
    profileId?: number;
  }>(),
  {
    visibleOptions: () => [],
  }
);

const visibleOptionsSafe = computed(() => props.visibleOptions ?? []);

const stats = ref<TWinSuggestion | null>(null);
const isLoadingStats = ref(false);
const showOpponentBreakdown = ref(false);
let latestFetchGameId = 0;

async function loadGameStats(gameId?: number) {
  if (!props.leagueId || !gameId || gameId <= 0) {
    stats.value = null;
    isLoadingStats.value = false;
    return;
  }

  const reqGameId = gameId;
  latestFetchGameId = reqGameId;
  isLoadingStats.value = true;
  stats.value = null;

  try {
    const res = await fetchGameWinStats(
      props.leagueId,
      reqGameId,
      props.profileId
    );
    if (latestFetchGameId === reqGameId) {
      stats.value = res;
    }
  } catch (e) {
    console.error('Failed to fetch game matchup stats:', e);
  } finally {
    if (latestFetchGameId === reqGameId) {
      isLoadingStats.value = false;
    }
  }
}

watch(
  () => props.gameInformation?.game?.id,
  (newGameId) => {
    loadGameStats(newGameId);
  },
  { immediate: true }
);

function getWinChanceColor(chance: number) {
  if (chance >= 55) return 'positive';
  if (chance >= 45) return 'amber-9';
  return 'grey-7';
}

function getOpponentChanceClass(chance: number) {
  if (chance >= 55) return 'text-positive';
  if (chance >= 45) return 'text-amber-9';
  return 'text-grey-7';
}

function findSelectedOption(optionId: number) {
  // find selected option by game option id
  const found = props.gameSelection.selectedOptions.find(
    (o) => o.game_option === optionId
  );
  if (!found) {
    // If we can't find it, we should return a dummy object to avoid crashing
    // instead of throwing an error. This can happen if props are out of sync.
    return { value: false, choice: null };
  }
  return found;
}
</script>

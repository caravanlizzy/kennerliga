<template>
  <q-card flat unelevated class="player-card">
    <q-card-section class="card-body">
      <div class="game-primary-section">
        <template v-if="hasSelectedOrBanInfo">
          <!-- Games list (per game) -->
          <div
            v-for="(game, idx) in displayedSelectedGames"
            :key="gameKey(game, idx)"
            class="selected-game-card q-mb-md"
          >
            <!-- Game Header -->
            <div class="game-title-row">
              <UserAvatar
                class="player-avatar-inline"
                :display-username="member.username"
                size="48px"
                shape="squircle"
              />
              <div class="game-title-highlight">
                <div class="game-title">
                  <span class="game-name-text">
                    {{ game.game_name }}
                    <KennerTooltip v-if="(game.game_name || '').length > 28">
                      {{ game.game_name }}
                    </KennerTooltip>
                  </span>
                </div>
              </div>
              <KennerButton
                flat
                round
                size="sm"
                icon="expand_more"
                class="expand-btn"
                :class="{ expanded: isExpanded(idx) }"
                @click="toggleExpanded(idx)"
              />
            </div>

            <!-- Expandable Settings (per game) -->
            <transition name="expand">
              <div v-if="isExpanded(idx)" class="game-settings-wrapper">
                <div class="settings-divider"></div>
                <GameSettingsDisplay :selectedOptions="game.selected_options" />
              </div>
            </transition>
          </div>

          <!-- Bans Section (ONCE per player) -->
          <div class="bans-section">
            <div class="ban-row">
              <div class="bans-label">
                <q-icon name="gavel" size="16px" />
                <span>Ban</span>
              </div>
              <div class="bans-content">
                <q-chip v-if="myBannedGameName" dense class="my-ban-chip">
                  {{ myBannedGameName }}
                </q-chip>
                <span v-else-if="member.has_banned" class="no-bans">
                  Ban skipped
                </span>
              </div>
            </div>

            <div v-if="firstGameSelectionBannedByOthers" class="ban-row">
              <div class="bans-label">
                <q-icon name="group" size="16px" />
                <span>Banned Pick</span>
              </div>
              <div class="bans-content">
                <template v-if="firstGameSelectionBannedByOthers">
                  <q-chip dense class="first-selection-chip" icon="looks_one">
                    {{ firstGameSelectionBannedByOthers }}
                  </q-chip>
                </template>
              </div>
            </div>
          </div>
        </template>

        <!-- Empty State (only when no selected games AND no ban info) -->
        <div v-else class="no-game-selected row items-center">
          <q-icon name="videogame_asset_off" size="32px" />
          <div class="q-ml-sm">
            <div class="text-grey-8">{{ member.profile_name }}</div>
            No game selected
          </div>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import UserAvatar from 'components/ui/UserAvatar.vue';
import GameSettingsDisplay from 'components/game/selectedGame/GameSettingsDisplay.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';

import { TLeagueMemberDto, TSelectedGameOptionDto } from 'src/types';

type SelectedGame = {
  id?: number | string;
  game_name?: string;
  selected_options?: TSelectedGameOptionDto[];
};

const props = withDefaults(
  defineProps<{ member: TLeagueMemberDto; color?: string }>(),
  {
    color: 'var(--q-dark)',
  }
);

const expandedByIndex = ref<Record<number, boolean>>({});

function toggleExpanded(idx: number) {
  expandedByIndex.value[idx] = !expandedByIndex.value[idx];
}
function isExpanded(idx: number) {
  return !!expandedByIndex.value[idx];
}
function gameKey(game: SelectedGame, idx: number) {
  return game?.id ?? idx;
}

const banners = computed(() => props.member.banned_by ?? []);

const myBannedGameName = computed(() => {
  const mbg = props.member?.my_banned_game;
  return mbg?.game_name ?? null;
});

const firstGameSelectionBannedByOthers = computed(() => {
  const fgs = props.member?.first_game_selection_banned_by_others;
  return fgs?.game_name ?? fgs?.game?.game_name ?? null;
});

const hasSelectedGames = computed(
  () => (props.member?.selected_games?.length ?? 0) > 0
);

const displayedSelectedGames = computed<SelectedGame[]>(() => {
  const selected = (props.member?.selected_games ?? []) as SelectedGame[];
  if (selected.length > 0) return selected;

  if (firstGameSelectionBannedByOthers.value) {
    return [
      {
        id: 'banned-pick-placeholder',
        game_name: firstGameSelectionBannedByOthers.value,
        selected_options: [],
      },
    ];
  }

  return [];
});

const hasBanInfo = computed(() => {
  return (
    Boolean(myBannedGameName.value) ||
    Boolean(firstGameSelectionBannedByOthers.value) ||
    (banners.value?.length ?? 0) > 0
  );
});

const hasSelectedOrBanInfo = computed(
  () => hasSelectedGames.value || hasBanInfo.value
);
</script>

<style scoped lang="scss">
.player-card {
  padding: 16px;
}

/* GAME TITLE ROW */
.game-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.player-avatar-inline {
  flex-shrink: 0;
}

.game-title-highlight {
  flex: 1;
  padding: 6px 0;
  position: relative;
  /* No border, no background = clean */
}

.game-title-highlight::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 3px;
  background: #3dadea; /* primary color */
  border-radius: 3px;
}

.game-name-text {
  font-size: 18px;
  font-weight: 700;
  color: #222;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* CHIPS – clean white with soft gray border */
.q-chip {
  background: #fff !important;
  border: 1px solid #e5e7eb !important;
  font-size: 13px;
  padding: 4px 10px !important;
  border-radius: 8px !important;
}

/* RED CHIP */
.my-ban-chip {
  color: #dc2626 !important;
  border-color: #fecaca !important;
}

/* BLUE CHIP */
.first-selection-chip {
  color: #1e3a8a !important;
  border-color: #bfdbfe !important;
}

/* BANS SECTION – no background, no border */
.bans-section {
  margin-top: 6px;
}

.ban-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 4px;
}

.bans-label {
  width: 110px;
  font-size: 12px;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 6px;
}

.no-bans {
  color: #9ca3af;
  font-style: italic;
}
</style>

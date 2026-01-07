<template>
  <q-card flat unelevated class="player-card">
    <q-card-section class="card-body">
      <div class="game-primary-section">
        <div v-for="m in allMembers" :key="m.id" class="member-group q-mb-xl">
          <!-- Member Header -->
          <div class="member-header q-mb-md">
            <UserAvatar
              :display-username="m.username"
              size="48px"
              shape="squircle"
            />
            <div class="member-info q-ml-md">
              <div class="text-h6 text-weight-bold">{{ m.profile_name }}</div>
            </div>
          </div>

          <!-- 1. Active Pick(s) -->
          <div
            v-for="game in getActivePicks(m)"
            :key="game.id"
            class="selected-game-card q-mb-md"
          >
            <div class="game-title-row">
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
                :class="{ expanded: isExpanded(game.id) }"
                @click="toggleExpanded(game.id)"
              />
            </div>

            <transition name="expand">
              <div v-if="isExpanded(game.id)" class="game-settings-wrapper">
                <div class="settings-divider"></div>
                <GameSettingsDisplay :selectedOptions="game.selected_options" />
              </div>
            </transition>
          </div>

          <!-- 2. The Game they Banned (my_banned_game) -->
          <div v-if="m.my_banned_game?.game" class="ban-row q-mb-md">
            <div class="bans-label">
              <q-icon name="gavel" size="16px" color="red-5" />
              <span>Banned</span>
            </div>
            <div class="bans-content">
              <q-chip dense class="my-ban-chip">
                {{ m.my_banned_game.game_name }}
                <KennerTooltip v-if="getOwnerName(m.my_banned_game.profile)">
                  Picked by {{ getOwnerName(m.my_banned_game.profile) }}
                </KennerTooltip>
              </q-chip>
            </div>
          </div>
          <div v-else-if="m.has_banned" class="ban-row q-mb-md">
            <div class="bans-label">
              <q-icon name="gavel" size="16px" />
              <span>Ban</span>
            </div>
            <div class="bans-content">
              <span class="no-bans">Ban skipped</span>
            </div>
          </div>

          <!-- 3. Their own game that has been successfully banned -->
          <div
            v-for="game in getSuccessfullyBannedPicks(m)"
            :key="'banned-' + game.id"
            class="selected-game-card q-mb-md banned-pick-row"
          >
            <div class="game-title-row">
              <div class="game-title-highlight banned">
                <div class="game-title">
                  <span class="game-name-text text-grey-6">
                    <q-icon
                      name="block"
                      color="red-5"
                      size="xs"
                      class="q-mr-xs"
                    />
                    <del>{{ game.game_name }}</del>
                  </span>
                </div>
                <div class="text-caption text-grey-6">
                  Successfully Banned
                  <span v-if="getBannerNames(game.id).length > 0">
                    by
                    <strong>{{
                      formatBannerNames(getBannerNames(game.id))
                    }}</strong>
                  </span>
                </div>
              </div>
              <KennerButton
                flat
                round
                size="sm"
                icon="expand_more"
                class="expand-btn"
                :class="{ expanded: isExpanded(game.id) }"
                @click="toggleExpanded(game.id)"
              />
            </div>

            <transition name="expand">
              <div v-if="isExpanded(game.id)" class="game-settings-wrapper">
                <div class="settings-divider"></div>
                <div class="opacity-50">
                  <GameSettingsDisplay :selectedOptions="game.selected_options" />
                </div>
              </div>
            </transition>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="allMembers.length === 0" class="no-game-selected row items-center">
          <q-icon name="videogame_asset_off" size="32px" />
          <div class="q-ml-sm">
            No players in league
          </div>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import UserAvatar from 'components/ui/UserAvatar.vue';
import GameSettingsDisplay from 'components/game/selectedGame/GameSettingsDisplay.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';

import { TSeasonParticipantDto } from 'src/types';

const props = withDefaults(
  defineProps<{
    allMembers?: TSeasonParticipantDto[];
    color?: string;
  }>(),
  {
    allMembers: () => [],
    color: 'var(--q-dark)',
  }
);

const expandedById = ref<Record<number, boolean>>({});

function toggleExpanded(id: number) {
  expandedById.value[id] = !expandedById.value[id];
}
function isExpanded(id: number) {
  return !!expandedById.value[id];
}

function getActivePicks(m: TSeasonParticipantDto) {
  return (m.selected_games ?? []).filter((g) => !g.successfully_banned);
}

function getSuccessfullyBannedPicks(m: TSeasonParticipantDto) {
  return (m.selected_games ?? []).filter((g) => g.successfully_banned);
}

function getOwnerName(profileId: number) {
  const owner = props.allMembers?.find((m) => m.profile === profileId);
  return owner?.profile_name ?? null;
}

function getBannerNames(gameId: number) {
  return (props.allMembers ?? [])
    .filter((m) => m.my_banned_game?.game && m.my_banned_game.id === gameId)
    .map((m) => m.profile_name);
}

function formatBannerNames(names: string[]) {
  if (names.length === 0) return '';
  if (names.length === 1) return names[0];
  if (names.length === 2) return `${names[0]} and ${names[1]}`;
  return `${names.slice(0, -1).join(', ')} and ${names[names.length - 1]}`;
}
</script>

<style scoped lang="scss">
.player-card {
  padding: 16px;
}

/* MEMBER HEADER */
.member-header {
  display: flex;
  align-items: center;
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

.opacity-50 {
  opacity: 0.5;
}

.game-title-highlight {
  flex: 1;
  padding: 6px 0;
  position: relative;
  /* No border, no background = clean */
}

.game-title-highlight.banned::after {
  background: var(--q-negative);
}

.game-title-highlight::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 3px;
  background: var(--q-info); /* info color */
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

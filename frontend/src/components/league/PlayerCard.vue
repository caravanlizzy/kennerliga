<template>
  <div class="player-card">
    <div v-for="m in allMembers" :key="m.id" class="member-section">
      <!-- Member Header -->
      <div class="member-header">
        <UserAvatar
          :display-username="m.username"
          :subtitle="m.profile_name !== m.username ? m.profile_name : undefined"
          :shape="getMemberShape(m)"
          :color="getMemberColor(m)"
          size="40px"
        />
        <div class="header-content q-ml-md">
          <div class="text-subtitle1 text-weight-bold player-name">
            {{ m.profile_name }}
          </div>
          <div v-if="m.has_banned && !m.my_banned_game?.game" class="text-caption text-grey-6 italic">
            Skipped ban
          </div>
        </div>
      </div>

      <q-list class="game-list">
        <!-- 1. Active Pick(s) -->
        <div
          v-for="game in getActivePicks(m)"
          :key="game.id"
          class="game-item-container"
        >
          <q-item class="game-item">
            <q-item-section avatar>
              <div class="game-icon-bg">
                <q-icon name="sports_esports" color="primary" size="20px" />
              </div>
            </q-item-section>

            <q-item-section>
              <q-item-label class="game-name">
                {{ game.game_name }}
                <KennerTooltip v-if="(game.game_name || '').length > 28">
                  {{ game.game_name }}
                </KennerTooltip>
              </q-item-label>
              <q-item-label v-if="game.platform_name" caption class="platform-label">
                {{ game.platform_name }}
              </q-item-label>
            </q-item-section>

            <q-item-section side>
              <KennerButton
                flat
                round
                size="sm"
                color="grey-6"
                :icon="isExpanded(game.id) ? 'expand_less' : 'expand_more'"
                @click="toggleExpanded(game.id)"
              />
            </q-item-section>
          </q-item>

          <q-slide-transition>
            <div v-if="isExpanded(game.id)" class="game-details q-px-md q-pb-md">
              <GameSettingsDisplay :selectedOptions="game.selected_options" />
            </div>
          </q-slide-transition>
        </div>

        <!-- 2. The Game they Banned (The Action they took) -->
        <q-item v-if="m.my_banned_game?.game" class="ban-action-item">
          <q-item-section avatar>
            <q-icon name="gavel" color="blue-grey-4" size="18px" />
          </q-item-section>
          <q-item-section>
            <q-item-label class="row items-center ban-text">
              <span class="text-blue-grey-6 q-mr-xs">Banned</span>
              <span class="text-weight-medium text-blue-grey-8">{{ m.my_banned_game.game_name }}</span>
              <KennerTooltip v-if="getOwnerName(m.my_banned_game.profile)">
                Picked by {{ getOwnerName(m.my_banned_game.profile) }}
              </KennerTooltip>
            </q-item-label>
          </q-item-section>
        </q-item>

        <!-- 3. Their own game that has been successfully banned (The State of their pick) -->
        <div
          v-for="game in getSuccessfullyBannedPicks(m)"
          :key="'banned-' + game.id"
          class="game-item-container banned"
        >
          <q-item class="game-item">
            <q-item-section avatar>
              <div class="game-icon-bg banned">
                <q-icon name="block" color="negative" size="18px" />
              </div>
            </q-item-section>

            <q-item-section>
              <q-item-label class="game-name text-grey-5 text-strike">
                {{ game.game_name }}
              </q-item-label>
              <q-item-label caption class="banned-by-label">
                Banned
                <span v-if="getBannerNames(game.id).length > 0">
                  by {{ formatBannerNames(getBannerNames(game.id)) }}
                </span>
              </q-item-label>
            </q-item-section>

            <q-item-section side>
              <KennerButton
                flat
                round
                size="sm"
                color="grey-4"
                :icon="isExpanded(game.id) ? 'expand_less' : 'expand_more'"
                @click="toggleExpanded(game.id)"
              />
            </q-item-section>
          </q-item>

          <q-slide-transition>
            <div v-if="isExpanded(game.id)" class="game-details q-px-md q-pb-md opacity-50">
              <GameSettingsDisplay :selectedOptions="game.selected_options" />
            </div>
          </q-slide-transition>
        </div>
      </q-list>
    </div>

    <!-- Empty State -->
    <div v-if="allMembers.length === 0" class="no-game-selected row items-center justify-center q-pa-xl">
      <q-icon name="videogame_asset_off" size="48px" color="grey-4" />
      <div class="text-h6 text-grey-5 q-mt-md full-width text-center">
        No players in league
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import UserAvatar from 'components/ui/UserAvatar.vue';
import GameSettingsDisplay from 'components/game/selectedGame/GameSettingsDisplay.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import { useUserStore } from 'stores/userStore';

import { TSeasonParticipantDto } from 'src/types';

const userStore = useUserStore();

function getMemberShape(m: TSeasonParticipantDto) {
  if (
    userStore.isMe(m.username) ||
    (userStore.user?.profile_id && m.profile === userStore.user.profile_id)
  ) {
    return userStore.user?.avatar_shape || m.avatar_shape;
  }
  return m.avatar_shape;
}

function getMemberColor(m: TSeasonParticipantDto) {
  if (
    userStore.isMe(m.username) ||
    (userStore.user?.profile_id && m.profile === userStore.user.profile_id)
  ) {
    return userStore.user?.avatar_color !== undefined
      ? userStore.user.avatar_color
      : m.avatar_color;
  }
  return m.avatar_color;
}

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
  padding: 0;
  display: flex;
  flex-direction: column;
}

.member-section {
  background: transparent;
  padding: 16px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);

  &:first-child {
    padding-top: 0;
  }

  &:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }
}

.member-header {
  display: flex;
  align-items: center;
  padding: 4px 8px 10px 8px;
}

.player-name {
  font-size: 1.05rem;
  letter-spacing: -0.01em;
  color: var(--q-dark);
}

.game-list {
  background: transparent;
}

.game-item-container {
  border-bottom: 1px solid rgba(0, 0, 0, 0.03);
  &:last-child {
    border-bottom: none;
  }
}

.game-item {
  padding: 8px 8px;
  min-height: 48px;
  border-radius: 8px;
  transition: background-color 0.2s ease;

  &:hover {
    background: rgba(0, 0, 0, 0.02);
  }
}

.game-icon-bg {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: rgba(var(--q-primary), 0.08);
  display: flex;
  align-items: center;
  justify-content: center;

  &.banned {
    background: rgba(var(--q-negative), 0.08);
  }
}

.game-name {
  font-size: 14.5px;
  font-weight: 600;
  color: #2c3e50;
  line-height: 1.2;
}

.platform-label {
  color: #7f8c8d;
  font-weight: 500;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  margin-top: 2px;
}

.ban-action-item {
  min-height: 40px;
  padding: 6px 8px;
  background: rgba(var(--q-blue-grey), 0.03);
  border-radius: 6px;
  margin: 4px 0;
}

.ban-text {
  font-size: 13px;
}

.banned-by-label {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
}

.game-details {
  border-top: 1px dashed rgba(0, 0, 0, 0.06);
  background: rgba(0, 0, 0, 0.01);
  margin: 0 4px;
  border-radius: 6px;
}

.opacity-50 {
  opacity: 0.6;
}

.text-strike {
  text-decoration: line-through;
  text-decoration-thickness: 1.5px;
}
</style>

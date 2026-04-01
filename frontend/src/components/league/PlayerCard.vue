<template>
  <div class="player-card">
    <div v-for="m in allMembers" :key="m.id" class="member-section">
      <!-- Member Header -->
      <div class="member-header">
        <UserAvatar
          :display-username="m.username"
          :subtitle="m.profile_name !== m.username ? m.profile_name : undefined"
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
  padding: 8px 0;
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;

  @media (min-width: 1024px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.member-section {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);

  &:hover {
    box-shadow: 0 12px 30px -5px rgba(0, 0, 0, 0.04), 0 8px 10px -6px rgba(0, 0, 0, 0.04);
  }
}

.member-header {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(to right, rgba(var(--q-primary), 0.03), transparent);
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}


.player-name {
  font-size: 1.1rem;
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
  padding: 12px 20px;
  min-height: 56px;
}

.game-icon-bg {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(var(--q-primary), 0.08);
  display: flex;
  align-items: center;
  justify-content: center;

  &.banned {
    background: rgba(var(--q-negative), 0.08);
  }
}

.game-name {
  font-size: 15px;
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
  min-height: 44px;
  padding: 8px 20px;
  background: rgba(var(--q-blue-grey), 0.03);
  border-top: 1px solid rgba(0, 0, 0, 0.02);
  border-bottom: 1px solid rgba(0, 0, 0, 0.02);
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
  margin: 0 10px;
  border-radius: 0 0 8px 8px;
}

.opacity-50 {
  opacity: 0.6;
}

.text-strike {
  text-decoration: line-through;
  text-decoration-thickness: 1.5px;
}
</style>

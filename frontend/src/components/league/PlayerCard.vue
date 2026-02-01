<template>
  <div class="player-card">
    <div v-for="m in allMembers" :key="m.id" class="member-section">
      <!-- Member Header -->
      <div class="member-header q-mb-sm">
        <UserAvatar
          :display-username="m.username"
          size="32px"
        />
        <div class="text-subtitle1 text-weight-bold q-ml-sm text-primary">
          {{ m.profile_name }}
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
              <q-icon name="sports_esports" color="primary" size="24px" />
            </q-item-section>

            <q-item-section>
              <q-item-label class="game-name">
                {{ game.game_name }}
                <KennerTooltip v-if="(game.game_name || '').length > 28">
                  {{ game.game_name }}
                </KennerTooltip>
              </q-item-label>
              <q-item-label v-if="game.platform_name" caption class="text-grey-7 text-weight-medium">
                {{ game.platform_name }}
              </q-item-label>
            </q-item-section>

            <q-item-section side>
              <KennerButton
                flat
                round
                size="sm"
                :icon="isExpanded(game.id) ? 'expand_less' : 'expand_more'"
                @click="toggleExpanded(game.id)"
              />
            </q-item-section>
          </q-item>

          <q-slide-transition>
            <div v-if="isExpanded(game.id)" class="game-details q-px-md q-pb-sm">
              <GameSettingsDisplay :selectedOptions="game.selected_options" />
            </div>
          </q-slide-transition>
        </div>

        <!-- 2. The Game they Banned -->
        <q-item v-if="m.my_banned_game?.game" class="ban-item">
          <q-item-section avatar>
            <q-icon name="gavel" color="blue-grey-4" size="20px" />
          </q-item-section>
          <q-item-section>
            <q-item-label class="row items-center">
              <span class="text-blue-grey-7 text-weight-medium q-mr-sm">Banned:</span>
              <span class="text-weight-medium">{{ m.my_banned_game.game_name }}</span>
              <KennerTooltip v-if="getOwnerName(m.my_banned_game.profile)">
                Picked by {{ getOwnerName(m.my_banned_game.profile) }}
              </KennerTooltip>
            </q-item-label>
            <q-item-label v-if="m.my_banned_game.platform_name" caption class="text-blue-grey-4">
              {{ m.my_banned_game.platform_name }}
            </q-item-label>
          </q-item-section>
        </q-item>

        <q-item v-else-if="m.has_banned" class="ban-item skipped">
          <q-item-section avatar>
            <q-icon name="gavel" color="grey-5" size="20px" />
          </q-item-section>
          <q-item-section>
            <q-item-label class="text-grey-6 italic">Player skipped ban</q-item-label>
          </q-item-section>
        </q-item>

        <!-- 3. Their own game that has been successfully banned -->
        <div
          v-for="game in getSuccessfullyBannedPicks(m)"
          :key="'banned-' + game.id"
          class="game-item-container banned"
        >
          <q-item class="game-item">
            <q-item-section avatar>
              <q-icon name="block" color="negative" size="20px" />
            </q-item-section>

            <q-item-section>
              <q-item-label class="game-name text-grey-6 text-strike">
                {{ game.game_name }}
              </q-item-label>
              <q-item-label v-if="game.platform_name" caption class="text-grey-5 text-strike" style="margin-top: -2px;">
                {{ game.platform_name }}
              </q-item-label>
              <q-item-label caption class="text-blue-grey-4">
                Successfully Banned
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
                :icon="isExpanded(game.id) ? 'expand_less' : 'expand_more'"
                @click="toggleExpanded(game.id)"
              />
            </q-item-section>
          </q-item>

          <q-slide-transition>
            <div v-if="isExpanded(game.id)" class="game-details q-px-md q-pb-sm opacity-50">
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
  gap: 16px;

  @media (min-width: 1024px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.member-section {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);

  &:hover {
    border-color: var(--q-primary);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  }
}

.member-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: rgba(var(--q-primary), 0.05);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
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
  padding: 8px 16px;
  min-height: 48px;
}

.game-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--q-dark);
}

.ban-item {
  min-height: 40px;
  padding: 4px 16px;
  background: rgba(var(--q-blue-grey), 0.05);
  border-bottom: 1px solid rgba(0, 0, 0, 0.03);

  &.skipped {
    background: transparent;
  }
}

.game-details {
  border-top: 1px dashed rgba(0, 0, 0, 0.05);
  background: rgba(0, 0, 0, 0.01);
}

.opacity-50 {
  opacity: 0.5;
}

.text-strike {
  text-decoration: line-through;
}
</style>

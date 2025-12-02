<template>
  <q-card
    flat
    class="player-card"
    :class="{ 'active-player': member.is_active_player }"
  >
    <!-- Animated background orbs -->
    <div class="background-orbs">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
    </div>

    <!-- Header with glassmorphism -->
    <div class="card-header">
      <div class="header-content">
        <!-- Avatar with glow effect -->
        <div
          class="avatar-wrapper"
          :class="{ 'avatar-active': member.is_active_player }"
        >
          <UserAvatar
            :display-username="member.username"
            size="56px"
            shape="circle"
          />
          <div v-if="member.is_active_player" class="active-indicator">
            <q-icon name="bolt" size="14px" color="white" />
          </div>
          <div v-if="member.is_active_player" class="avatar-glow"></div>
        </div>

        <!-- Name and Status -->
        <div class="player-info">
          <div class="player-name">
            {{ member.username }}
          </div>
        </div>

        <!-- Decorative element -->
        <div class="header-decoration">
          <q-icon name="sports_esports" size="80px" class="decoration-icon" />
        </div>
      </div>
    </div>

    <!-- Body Content -->
    <q-card-section class="card-body">
      <div class="game-info-section">
        <div class="selected-game-card" v-if="member.selected_game">
          <!-- Game Header -->
          <div class="game-header">
            <div class="game-title-row">
              <div class="game-icon-wrapper">
                <q-icon name="sports_esports" size="20px" />
              </div>
              <div class="game-title">
                {{ truncateString(member.selected_game.game_name) }}
                <q-tooltip
                  v-if="(member.selected_game.game_name || '').length > 28"
                >
                  {{ member.selected_game.game_name }}
                </q-tooltip>
              </div>
              <q-btn
                flat
                round
                size="sm"
                icon="expand_more"
                class="expand-btn"
                :class="{ expanded: isExpanded }"
                @click="isExpanded = !isExpanded"
              />
            </div>

            <!-- Bans Section -->
            <div class="bans-section">
              <!-- Player's Own Ban -->
              <div class="ban-row">
                <div class="bans-label">
                  <q-icon name="gavel" size="16px" />
                  <span>My Ban</span>
                </div>
                <div class="bans-content">
                  <q-chip
                    v-if="myBannedGameName"
                    dense
                    class="my-ban-chip"
                    icon="block"
                  >
                    {{ myBannedGameName }}
                    <q-tooltip>Game this player chose to ban</q-tooltip>
                  </q-chip>
                  <span v-else class="no-bans">None</span>
                </div>
              </div>
              <!-- Banned by Others -->
              <div class="ban-row">
                <div class="bans-label">
                  <q-icon name="group" size="16px" />
                  <span>Banned By</span>
                </div>
                <div class="bans-content">
                  <template v-if="banners.length">
                    <div class="banners-avatars">
                      <UserAvatar
                        v-for="(name, idx) in banners"
                        :key="idx"
                        :display-username="name"
                        size="28px"
                        class="banner-avatar"
                      />
                      <q-tooltip>Players who banned this game</q-tooltip>
                    </div>
                    <q-chip
                      v-if="firstGameSelection"
                      dense
                      class="first-selection-chip q-ml-sm"
                      icon="looks_one"
                    >
                      {{ firstGameSelection }}
                      <q-tooltip>First game selection</q-tooltip>
                    </q-chip>
                  </template>
                  <span v-else class="no-bans">None</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Expandable Settings -->
          <transition name="expand">
            <div v-if="isExpanded" class="game-settings-wrapper">
              <div class="settings-divider"></div>
              <GameSettingsDisplay
                :selectedOptions="member.selected_game.selected_options"
              />
            </div>
          </transition>
        </div>

        <!-- Empty State -->
        <div v-else class="no-game-selected">
          <q-icon name="videogame_asset_off" size="32px" />
          <span>No game selected</span>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import UserAvatar from 'components/ui/UserAvatar.vue';
import { truncateString } from 'src/helpers';
import GameSettingsDisplay from 'components/game/selectedGame/GameSettingsDisplay.vue';

const props = withDefaults(defineProps<{ member: any; color?: string }>(), {
  color: 'var(--q-primary)',
});

const isExpanded = ref(false);
const banners = computed(() => props.member.banned_by ?? []);

const myBannedGameName = computed(() => {
  const mbg = props.member?.my_banned_game;
  return mbg?.game_name ?? null;
});

const firstGameSelection = computed(() => {
  const fgs = props.member?.first_game_selection;
  return fgs?.game_name ?? fgs?.game?.game_name ?? null;
});
</script>

<style scoped lang="scss">
.player-card {
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: linear-gradient(
    145deg,
    rgba(255, 255, 255, 0.95) 0%,
    rgba(255, 255, 255, 0.85) 100%
  );
  backdrop-filter: blur(20px);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04);
  position: relative;
}

.player-card.active-player {
  border-color: rgba(var(--q-positive-rgb, 33, 186, 69), 0.4);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06),
    0 0 0 1px rgba(var(--q-positive-rgb, 33, 186, 69), 0.2),
    0 0 30px rgba(var(--q-positive-rgb, 33, 186, 69), 0.1);

  &:hover {
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12),
      0 0 0 1px rgba(var(--q-positive-rgb, 33, 186, 69), 0.3),
      0 0 40px rgba(var(--q-positive-rgb, 33, 186, 69), 0.15);
  }
}

/* Background orbs */
.background-orbs {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.5;
  animation: float 8s ease-in-out infinite;
}

.orb-1 {
  width: 150px;
  height: 150px;
  background: rgba(var(--q-primary-rgb), 0.15);
  top: -50px;
  right: -30px;
  animation-delay: 0s;
}

.orb-2 {
  width: 100px;
  height: 100px;
  background: rgba(var(--q-secondary-rgb), 0.1);
  bottom: -30px;
  left: -20px;
  animation-delay: -4s;
}

@keyframes float {
  0%,
  100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(10px, -10px) scale(1.05);
  }
}

/* Header Section */
.card-header {
  padding: 24px 20px;
  position: relative;
  overflow: hidden;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
  z-index: 1;
}

.header-decoration {
  position: absolute;
  right: -20px;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0.04;
  pointer-events: none;
}

/* Avatar styles */
.avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.avatar-active {
  .avatar-glow {
    position: absolute;
    inset: -4px;
    border-radius: 50%;
    background: radial-gradient(
      circle,
      rgba(var(--q-positive-rgb, 33, 186, 69), 0.3) 0%,
      transparent 70%
    );
    animation: glow-pulse 2s ease-in-out infinite;
  }
}

@keyframes glow-pulse {
  0%,
  100% {
    opacity: 0.6;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.1);
  }
}

.active-indicator {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--q-positive) 0%, #2ecc71 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid white;
  box-shadow: 0 2px 8px rgba(var(--q-positive-rgb, 33, 186, 69), 0.4);
  z-index: 2;
}

/* Player Info */
.player-info {
  flex: 1;
  min-width: 0;
}

.player-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--q-dark);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: -0.02em;
}

.player-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--q-positive);
  animation: status-pulse 1.5s ease-in-out infinite;
}

@keyframes status-pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.status-text {
  font-size: 12px;
  font-weight: 500;
  color: var(--q-positive);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Body Section */
.card-body {
  padding: 0 20px 20px;
}

.game-info-section {
  margin-top: 0;
}

.selected-game-card {
  background: rgba(0, 0, 0, 0.02);
  border-radius: 16px;
  padding: 16px;
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.game-header {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.game-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.game-icon-wrapper {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(var(--q-primary-rgb), 0.08);
  border: 1.5px solid rgba(var(--q-primary-rgb), 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--q-primary);
  flex-shrink: 0;
}

.game-title {
  flex: 1;
  font-size: 15px;
  font-weight: 600;
  color: var(--q-dark);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.expand-btn {
  color: var(--q-grey-6);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &.expanded {
    transform: rotate(180deg);
    color: var(--q-primary);
  }

  &:hover {
    background: rgba(var(--q-primary-rgb), 0.1);
  }
}

/* Bans Section */
.bans-section {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: 10px;
}

.bans-label {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--q-grey-7);
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.bans-content {
  flex: 1;
  display: flex;
  align-items: center;
}

.banned-chip {
  background: rgba(239, 68, 68, 0.1) !important;
  color: #dc2626 !important;
  font-size: 12px;
  font-weight: 500;
}

.banners-avatars {
  display: flex;
  margin-left: -4px;

  .banner-avatar {
    margin-left: -8px;
    border: 2px solid white;
    border-radius: 50%;

    &:first-child {
      margin-left: 0;
    }
  }
}

.no-bans {
  color: var(--q-grey-5);
  font-size: 13px;
  font-style: italic;
}

/* Expandable Settings */
.game-settings-wrapper {
  overflow: hidden;
}

.settings-divider {
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(0, 0, 0, 0.08) 50%,
    transparent 100%
  );
  margin: 16px 0;
}

/* Empty State */
.no-game-selected {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 32px;
  color: var(--q-grey-5);
  font-size: 14px;
}

/* Transitions */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 500px;
}
</style>

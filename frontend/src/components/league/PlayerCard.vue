<template>
  <q-card flat class="player-card" :class="{ 'active-player': member.is_active_player }">
    <!-- Header with gradient -->
    <div class="card-header">
      <div class="header-content">
        <!-- Avatar/Initial Circle -->
        <div class="player-avatar">
          <span class="avatar-text">{{ userInitial }}</span>
          <div v-if="member.is_active_player" class="active-indicator">
            <q-icon name="bolt" size="12px" />
          </div>
        </div>

        <!-- Name and Status -->
        <div class="player-info">
          <div class="player-name">
            {{ member.username }}
          </div>
          <div class="player-status">
            <q-badge
              v-if="member.is_active_player"
              color="positive"
              label="Active"
              class="status-badge"
            />
            <q-badge
              v-else
              color="grey-6"
              label="Inactive"
              class="status-badge"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Body Content -->
    <q-card-section class="card-body">
      <!-- Meta Info Chips -->
      <div v-if="member.selected_game || member.has_banned" class="meta-chips">
        <q-chip
          v-if="member.selected_game"
          dense
          color="positive"
          text-color="white"
          icon="sports_esports"
          size="sm"
        >
          Game Selected
        </q-chip>
        <q-chip
          v-if="member.has_banned"
          dense
          color="negative"
          text-color="white"
          icon="block"
          size="sm"
        >
          Ban Submitted
        </q-chip>
      </div>

      <!-- Selected Game Info -->
      <div class="game-info-section">
        <SelectedGameInfo :member="member" />
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import SelectedGameInfo from 'components/league/SelectedGameInfo.vue';

const props = withDefaults(
  defineProps<{ member: any; color?: string }>(),
  { color: 'var(--q-primary)' }
);

const userInitial = computed(() => {
  return props.member.username?.charAt(0).toUpperCase() || '?';
});
</script>

<style scoped>
.player-card {
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: var(--q-card-bg, #fff);
}


.player-card.active-player {
  border-color: var(--q-positive);
  box-shadow: 0 0 0 1px var(--q-positive);
}

/* Header Section */
.card-header {
  background: linear-gradient(135deg, rgba(var(--q-primary-rgb), 0.08) 0%, rgba(var(--q-secondary-rgb), 0.12) 100%);
  padding: 20px 16px;
  position: relative;
  overflow: hidden;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.card-header::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 200px;
  height: 200px;
  background: rgba(var(--q-primary-rgb), 0.03);
  border-radius: 50%;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
  z-index: 1;
}

/* Avatar */
.player-avatar {
  position: relative;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--q-primary) 0%, var(--q-secondary) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.avatar-text {
  font-size: 20px;
  font-weight: 600;
  color: white;
}

.active-indicator {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--q-positive);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

/* Player Info */
.player-info {
  flex: 1;
  min-width: 0;
}

.player-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--q-dark);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.player-status {
  display: flex;
  align-items: center;
}

.status-badge {
  font-size: 10px;
  padding: 2px 8px;
  font-weight: 500;
}

/* Body Section */
.card-body {
  padding: 16px;
}

.meta-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.game-info-section {
  margin-top: 8px;
}
</style>

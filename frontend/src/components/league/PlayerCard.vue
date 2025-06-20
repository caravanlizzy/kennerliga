<template>
  <div class="player-card">
    <!-- Colored Header -->
    <div class="card-header" :class="bgClass">
      <div class="row items-center text-weight-medium no-wrap">
        {{ member.username }}
        <div v-if="isActive" class="active-indicator q-ml-xs">
          <span class="dot" />
        </div>
      </div>

      <div class="row items-center q-gutter-xs no-wrap">
        <q-badge
          v-if="member.selected_game"
          class="badge neutral-badge"
        >
          <q-icon name="sports_esports" size="14px" class="q-mr-xs" />
          GAME
        </q-badge>

        <q-badge
          v-if="member.banned_game"
          class="badge neutral-badge"
        >
          <q-icon name="block" size="14px" class="q-mr-xs" />
          BAN
        </q-badge>
      </div>
    </div>

    <!-- Body -->
    <div class="card-body">
      <SelectedGameInfo
        :member="member"
        :status="status"
        :isActive="isActive"
        :isBannable="isBannable"
        :isBanning="isBanning"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import SelectedGameInfo from 'components/league/SelectedGameInfo.vue';

const props = defineProps<{
  member: any;
  isActive: boolean;
  status: string;
  isBanning: boolean;
  isBannable: boolean;
  index?: number;
}>();

const bgClass = computed(() => {
  const i = props.index ?? 0;
  const bgClasses = [
    'bg-player-1',
    'bg-player-2',
    'bg-player-3',
    'bg-player-4',
    'bg-player-5',
    'bg-player-6',
  ];
  return bgClasses[i % bgClasses.length];
});
</script>

<style scoped lang="scss">
.player-card {
  background: #f3f3f3;
  border-radius: 8px;
  margin: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.card-header {
  padding: 8px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
}

.card-body {
  padding: 12px;
  background: white;
}

.badge {
  font-size: 0.65rem;
  padding: 2px 8px;
  border-radius: 6px;
  display: flex;
  align-items: center;
}

.neutral-badge {
  background-color: rgba(255, 255, 255, 0.15);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  font-weight: 500;
}

.active-indicator {
  display: flex;
  align-items: center;
  margin-left: 7px;
}

.dot {
  height: 9px;
  width: 9px;
  border-radius: 50%;
  display: inline-block;
  background: white;
  animation: pulse 1.8s ease-in-out infinite;
}


@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.3);
    opacity: 0.5;
  }
}
</style>

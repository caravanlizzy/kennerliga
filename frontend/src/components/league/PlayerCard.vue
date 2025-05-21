<template>
  <div
    class="q-pa-md rounded-borders relative full-height"
    :style="{
      minHeight: '240px',
    }"
  >
    <!-- Header -->
    <div class="row items-center justify-between">
      <div class="text-subtitle1 text-weight-bold row items-center">
        {{ member.username }}

        <div v-if="isActive" class="q-ml-sm active-player-indicator">
          <span class="dot q-mr-xs" :class="activeBackgroundColor" />
        </div>
      </div>

      <div class="row q-gutter-xs items-center">
        <q-badge v-if="member.selected_game" color="primary" text-color="white">
          GAME
          <q-icon name="check" />
        </q-badge>
        <q-badge v-if="member.banned_game" color="negative" text-color="white">
          BAN
          <q-icon name="check" />
        </q-badge>
      </div>
    </div>
    <SelectedGameInfo
      @select-for-ban="emit('select-for-ban')"
      :member="member"
      :status="status"
      :isActive="isActive"
      :isBannable="isBannable"
      :isBanning="isBanning"
    ></SelectedGameInfo>
  </div>
</template>

<script setup lang="ts">
import SelectedGameInfo from 'components/league/SelectedGameInfo.vue';
import { computed } from 'vue';

const props = defineProps<{
  member: any;
  isActive: boolean;
  status: string;
  isBanning: boolean;
  isBannable: boolean;
}>();

const emit = defineEmits<{
  (e: 'select-for-ban'): void;
}>();

const activeBackgroundColor = computed(() => {
  return props.status === 'BANNING' ? 'bg-accent' : 'bg-secondary';
});
</script>

<style scoped>
.active-player-indicator {
  border-radius: 15px;
  font-size: 12px;
  display: flex;
  align-items: center;
  animation: fadePulse 2s infinite;
}

.dot {
  height: 12px;
  width: 12px;
  border-radius: 50%;
  display: inline-block;
  animation: pulse 1.4s infinite ease-in-out;
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.4);
    opacity: 0.6;
  }
}
</style>

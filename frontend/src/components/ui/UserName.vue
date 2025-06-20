<template>
  <q-avatar
    size="27px"
    class="user-avatar square"
    :class="[
      computedColorClass
    ]"
  >
    <div class="avatar-content">
      <span v-if="initials">{{ initials }}</span>
      <q-icon v-else name="person" size="18px" />
    </div>
    <KennerTooltip>{{ displayUsername }}</KennerTooltip>
  </q-avatar>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import KennerTooltip from 'components/base/KennerTooltip.vue';

const props = defineProps<{
  username?: string;
  variant?: 'default' | 'ban';
  colorClass?: string; // Optional override, e.g., 'bg-player-3'
}>();

const { user } = storeToRefs(useUserStore());

const displayUsername = computed(() => {
  return props.username || user.value?.username || '';
});

const initials = computed(() => {
  const name = displayUsername.value.trim();
  if (!name) return '';
  const parts = name.split(' ');
  return parts.map(p => p[0]?.toUpperCase()).join('').slice(0, 2);
});

// Compute fallback color class if not passed in
function hashStringToIndex(str: string, mod: number): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash) % mod;
}

const computedColorClass = computed(() => {
  if (props.colorClass) return props.colorClass;
  const username = displayUsername.value || '';
  const index = hashStringToIndex(username, 6) + 1;
  return `bg-player-${index} text-white`;
});
</script>

<style scoped>
.user-avatar {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.square {
  border-radius: 100%;
}

.avatar-content {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

</style>

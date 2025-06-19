<template>
  <q-avatar
    size="27px"
    class="user-avatar square"
    :class="{ 'ban-ring': variant === 'ban', 'normal-ring': variant !== 'ban' }"
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
}>();

const { user } = storeToRefs(useUserStore());

const displayUsername = computed(() => {
  return props.username || user.value?.username || '';
});

const initials = computed(() => {
  const name = displayUsername.value.trim();
  if (!name) return '';
  const parts = name.split(' ');
  if (parts.length === 1) return parts[0][0]?.toUpperCase();
  return parts[0][0]?.toUpperCase() + parts[1][0]?.toUpperCase();
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
  background: transparent !important;
  color: #333;
  border: 2px solid currentColor;
  padding: 0;
}

.square {
  border-radius: 100%;
}

/* Centering fix */
.avatar-content {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

/* Ring colors */
.normal-ring {
  color: #f76c9f;
}

.ban-ring {
  color: #d32f2f;
}
</style>

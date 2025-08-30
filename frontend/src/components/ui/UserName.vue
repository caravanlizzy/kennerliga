<template>
  <q-avatar size="27px" class="user-avatar text-white" :class="colorClass">
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

const props = withDefaults(defineProps<{
  username?: string;
  colorClass?: string;
}>(), {
  colorClass: 'bg-accent' // 👈 your default
});

const { user } = storeToRefs(useUserStore());

const displayUsername = computed(() => {
  return props.username || user.value?.username || '';
});

const initials = computed(() => {
  const name = displayUsername.value.trim();
  if (!name) return '';
  const parts = name.split(' ');
  return parts
    .map((p) => p[0]?.toUpperCase())
    .join('')
    .slice(0, 2);
});
</script>


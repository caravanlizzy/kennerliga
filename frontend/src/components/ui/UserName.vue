<template>
  <q-avatar
    color="accent"
    size="27px"
    text-color="white"
  >
    {{ displayUsername[0] }}
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
}>();

const { user } = storeToRefs(useUserStore());

const displayUsername = computed(() => {
  return props.username || user.value?.username || '';
});
</script>

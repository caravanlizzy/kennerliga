<template>
  <div
    v-if="hasContent"
    class="action-content q-pa-md q-mt-sm"
  >
    <div class="text-section">
      <div v-if="leadText" class="text-caption text-grey-6 text-uppercase letter-spacing-1 q-mb-xs">
        <component :is="leadText" />
      </div>
      <div
        v-if="subject"
        class="text-h6 text-dark text-weight-bold"
        style="line-height: 1.2"
      >
        <component :is="subject" />
      </div>
      <div
        v-if="hint"
        class="text-caption text-grey-7 q-mt-xs"
      >
        <component :is="hint" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useActionBar } from 'src/composables/actionBar';
import { useUserStore } from 'stores/userStore';
import { useLeagueStore } from 'stores/leagueStore';
import { storeToRefs } from 'pinia';
import { useRoute } from 'vue-router';

const { leadText, subject, hint } = useActionBar();
const { user } = storeToRefs(useUserStore());
const route = useRoute();

const myLeagueStore = computed(() => {
  if (!user.value?.myCurrentLeagueId) return null;
  return useLeagueStore(user.value.myCurrentLeagueId)();
});

const isMeActivePlayer = computed(() => myLeagueStore.value?.isMeActivePlayer);

const showLeagueInfo = computed(() => {
  const excluded = [
    'about', 'rules', 'feedback', 'announcements', 'release-notes', 'taskboard',
    'users', 'user-detail', 'invite-user', 'invitations'
  ];
  return !excluded.includes(route.name as string);
});

const hasContent = computed(() => {
  const hasCustomContent = leadText.value || subject.value || hint.value;
  const hasLeagueTurnInfo = showLeagueInfo.value && isMeActivePlayer.value;
  return hasCustomContent || hasLeagueTurnInfo;
});
</script>

<style scoped lang="scss">
.action-content {
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.04);
}

.text-section {
  flex: 1;
  min-width: 0;
}

.letter-spacing-1 {
  letter-spacing: 0.05em;
  font-weight: 700;
}
</style>

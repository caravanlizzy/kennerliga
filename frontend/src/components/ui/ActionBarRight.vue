<template>
  <div v-if="hasRightContent" class="row items-center no-wrap q-gutter-x-sm">
    <!-- Status Chip -->
    <q-badge
      v-if="showLeagueInfo && statusNoun"
      color="grey-1"
      text-color="grey-8"
      class="text-uppercase text-bold q-px-sm q-py-xs"
      style="border-radius: 6px; letter-spacing: 0.05em; font-size: 0.7rem; border: 1px solid rgba(0,0,0,0.05)"
    >
      <template v-if="loading">
        Loading
      </template>
      <template v-else>
        {{ statusNoun }}
      </template>
    </q-badge>

    <!-- Active Player Chip -->
    <q-chip
      v-if="showLeagueInfo && activePlayer"
      outline
      :color="isMeActivePlayer ? 'positive' : 'grey-7'"
      :text-color="isMeActivePlayer ? 'positive' : 'grey-8'"
      class="text-weight-bold q-ma-none"
      style="border-radius: 6px; font-size: 0.8rem;"
    >
      <q-icon :name="isMeActivePlayer ? 'bolt' : 'schedule'" size="16px" class="q-mr-xs" />
      <span v-if="!isMobile">
        <span v-if="isMeActivePlayer">Your turn</span>
        <span v-else>{{ activePlayer?.username }}'s turn</span>
      </span>
      <span v-else>
         {{ isMeActivePlayer ? 'You' : activePlayer?.username }}
      </span>
    </q-chip>

    <!-- Action Buttons -->
    <div
      v-if="actions.length && isMeActivePlayer"
      class="row items-center no-wrap q-gutter-x-xs"
    >
      <KennerButton
        v-for="a in actions"
        :key="a.name"
        :disabled="a.disabled"
        :color="a.buttonVariant || 'dark'"
        :icon="a.icon"
        size="sm"
        @click="handleAction(a)"
      >
        <span v-if="!isMobile">{{ a.name }}</span>
      </KennerButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useActionBar } from 'src/composables/actionBar';
import KennerButton from 'components/base/KennerButton.vue';
import { useLeagueStore } from 'stores/leagueStore';
import { storeToRefs } from 'pinia';
import { useResponsive } from 'src/composables/responsive';
import { useUserStore } from 'stores/userStore';
import { useRoute } from 'vue-router';

const { actions, reset } = useActionBar();
const { user } = storeToRefs(useUserStore());
const route = useRoute();

const myLeagueStore = computed(() => {
  if (!user.value?.myCurrentLeagueId) return null;
  return useLeagueStore(user.value.myCurrentLeagueId)();
});

const statusNoun = computed(() => myLeagueStore.value?.statusNoun);
const loading = computed(() => myLeagueStore.value?.loading);
const activePlayer = computed(() => myLeagueStore.value?.activePlayer);
const isMeActivePlayer = computed(() => myLeagueStore.value?.isMeActivePlayer);

const { isMobile } = useResponsive();

const showLeagueInfo = computed(() => {
  const excluded = [
    'about', 'rules', 'feedback', 'announcements', 'release-notes', 'taskboard',
    'users', 'user-detail', 'invite-user', 'invitations'
  ];
  return !excluded.includes(route.name as string);
});

const hasRightContent = computed(() => {
  const hasLeagueInfo = showLeagueInfo.value && (statusNoun.value || activePlayer.value);
  const hasActions = actions.value.length > 0 && isMeActivePlayer.value;
  return hasLeagueInfo || hasActions;
});

async function handleAction(action: any) {
  try {
    action.callback();
    if (action.autoReset) reset();
  } catch (e) {
    console.error(e);
  }
}
</script>

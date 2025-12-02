<template>
  <q-card
    bordered
    flat
    class="action-bar-card q-mb-md"
  >
    <!-- Status Header Row -->
    <div class="status-header q-pa-sm">
      <div class="row items-center no-wrap">
        <!-- Left spacer -->
        <div class="col"></div>

        <!-- Center: Status chip -->
        <div class="col-auto flex flex-center">
          <q-chip
            color="primary"
            text-color="primary"
            square
            outline
            dense
            class="bg-white text-uppercase text-bold"
          >
            <template v-if="loading">
              Loading
            </template>
            <template v-else>
              {{ statusNoun }}
            </template>
          </q-chip>
        </div>

        <!-- Right: Active player chip -->
        <div class="col flex justify-end">
          <q-chip
            v-if="activePlayer"
            color="positive"
            text-color="white"
            square
            dense
            class="text-weight-bold"
          >
            <q-icon name="schedule" size="14px" class="q-mr-xs" />
            <span v-if="isMeActivePlayer">Your turn</span>
            <span v-else>{{ activePlayer?.username }}'s turn</span>
          </q-chip>
        </div>
      </div>
    </div>

    <!-- Separator when active -->
    <q-separator v-if="isMeActivePlayer" />

    <!-- Action Content (only when it's your turn) -->
    <div
      v-if="isMeActivePlayer"
      class="action-content q-pa-md"
    >
      <div
        :class="[
          isMobile ? 'column q-gutter-sm' : 'row items-center justify-between',
        ]"
      >
        <!-- Text Content -->
        <div
          v-if="leadText || subject"
          class="text-section"
          :class="{ 'q-mb-sm': isMobile && !leadText }"
        >
          <div v-if="leadText" class="text-body2 text-grey-7 q-mb-xs">
            <component :is="leadText" />
          </div>
          <div
            v-if="subject"
            class="text-h6 text-primary text-weight-bold"
          >
            <component :is="subject" />
          </div>
        </div>

        <!-- Action Buttons -->
        <div
          v-if="actions.length"
          class="row items-center no-wrap q-gutter-xs"
        >
          <KennerButton
            v-for="a in actions"
            :key="a.name"
            :disabled="a.disabled"
            :color="a.buttonVariant || 'primary'"
            :icon="a.icon"
            @click="handleAction(a)"
          >
            {{ a.name }}
          </KennerButton>
        </div>
      </div>
    </div>
  </q-card>
</template>

<script setup lang="ts">
import { useActionBar } from 'src/composables/actionBar';
import KennerButton from 'components/base/KennerButton.vue';
import { useLeagueStore } from 'stores/leagueStore';
import { storeToRefs } from 'pinia';
import { useResponsive } from 'src/composables/reponsive';
import { useUserStore } from 'stores/userStore';

const { actions, leadText, subject, reset } = useActionBar();
const { user } = storeToRefs(useUserStore());
const myLeagueStore = useLeagueStore(user.value!.myCurrentLeagueId)();
const { activePlayer, isMeActivePlayer, statusNoun, loading } =
  storeToRefs(myLeagueStore);
const { isMobile } = useResponsive();

async function handleAction(action: any) {
  try {
    action.callback();
    if (action.autoReset) reset();
  } catch (e) {
    console.error(e);
  }
}
</script>

<style scoped lang="scss">
.action-bar-card {
  border-radius: 8px;
  overflow: hidden;
  background: white;
}

.status-header {
  background: linear-gradient(
      135deg,
      rgba(var(--q-primary-rgb), 0.06) 0%,
      rgba(var(--q-secondary-rgb), 0.08) 100%
  );
}

.action-content {
  background: white;
}

.text-section {
  flex: 1;
  min-width: 0;
}

@media (max-width: 599px) {
  .action-content .row.q-gutter-xs {
    width: 100%;

    :deep(.q-btn) {
      flex: 1;
    }
  }
}
</style>

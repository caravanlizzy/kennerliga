<template>
  <q-card
    bordered
    flat
    class="action-bar-card q-mb-md"
  >
    <!-- Status Header Row -->
    <div class="status-header q-pa-sm">
      <div class="row items-center no-wrap">
        <!-- Center: Status chip -->
        <div class="col flex items-center">
          <q-badge
            color="white"
            text-color="primary"
            class="text-uppercase text-bold q-px-sm q-py-xs shadow-1"
            style="border-radius: 4px; border: 1px solid rgba(0,0,0,0.05)"
          >
            <template v-if="loading">
              Loading
            </template>
            <template v-else>
              {{ statusNoun }}
            </template>
          </q-badge>
        </div>

        <!-- Right: Active player chip -->
        <div class="col-auto flex justify-end">
          <q-chip
            v-if="activePlayer"
            :color="isMeActivePlayer ? 'positive' : 'grey-4'"
            :text-color="isMeActivePlayer ? 'white' : 'dark'"
            class="text-weight-bold"
            style="border-radius: 8px"
          >
            <q-icon :name="isMeActivePlayer ? 'bolt' : 'schedule'" size="16px" class="q-mr-xs" />
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
      v-if="isMeActivePlayer || hint"
      class="action-content q-pa-md"
    >
      <div
        :class="[
          isMobile ? 'column q-gutter-sm' : 'row items-center justify-between',
        ]"
      >
        <!-- Text Content -->
        <div
          v-if="leadText || subject || hint"
          class="text-section"
        >
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

        <!-- Action Buttons -->
        <div
          v-if="actions.length"
          class="row items-center no-wrap q-gutter-xs"
        >
          <KennerButton
            v-for="a in actions"
            :key="a.name"
            :disabled="a.disabled"
            :color="a.buttonVariant || 'dark'"
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
import { useResponsive } from 'src/composables/responsive';
import { useUserStore } from 'stores/userStore';

const { actions, leadText, subject, hint, reset } = useActionBar();
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
  border-radius: 12px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(54, 64, 88, 0.1);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.06);
    background: rgba(255, 255, 255, 0.8);
  }
}

.status-header {
  background: rgba(248, 249, 250, 0.5);
  border-bottom: 1px solid rgba(54, 64, 88, 0.05);
}

.action-content {
  background: transparent;
}

.text-section {
  flex: 1;
  min-width: 0;
}

.letter-spacing-1 {
  letter-spacing: 0.05em;
  font-weight: 700;
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

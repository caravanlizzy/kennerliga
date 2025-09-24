<template>
  <!-- full-width wrapper so we can center the inner bar -->
  <div
    class="column actionBar q-ma-md q-mx-auto q-pa-sm q-px-md rounded-borders bg-grey-2"
  >
    <div
      v-if="activePlayer"
      class="row items-center justify-around status-line q-py-xs"
    >
      <!-- Status chip -->
      <q-chip
        color="primary"
        text-color="white"
        square
        dense
        class="text-uppercase text-bold"
      >
        {{ statusNoun }}
      </q-chip>

      <!-- Active player turn -->
      <div class="row items-center no-wrap text-subtitle1 text-italic">
        <q-chip
          :class="activePlayer?.colorClass"
          text-color="white"
          square
          dense
          class="q-mr-xs text-weight-bold"
        >
          {{ activePlayer?.username }}
        </q-chip>
        <span>'s turn</span>
      </div>
    </div>

    <q-separator v-if="isMeActivePlayer" inset spaced/>

    <div
      v-if="isMeActivePlayer"
      :class="[
        isMobile ? 'column' : 'row q-py-sm',
        'justify-between items-center no-wrap q-px-md',
      ]"
    >
      <div v-if="leadText" class="text-body2 text-primary q-mr-md">
        <component :is="leadText"/>
      </div>

      <div
        v-if="subject"
        class="text-body1 text-primary text-weight-bold q-mr-md"
      >
        <component :is="subject"/>
      </div>

      <div
        class="row items-center no-wrap q-gutter-xs"
        :class="{'q-mt-xs': isMobile }"
      >
        <kenner-button
          v-for="a in actions"
          :key="a.name"
          :outline="!a.buttonFilled"
          :color="a.buttonVariant || 'primary'"
          class="compact-btn q-px-sm q-py-xs text-caption"
          @click="handleAction(a)"
        >
          <q-icon v-if="a.icon" :name="a.icon" size="16px" class="q-mr-xs"/>
          <span class="btn-label">{{ a.name }}</span>
        </kenner-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useActionBar } from 'src/composables/actionBar';
import KennerButton from 'components/base/KennerButton.vue';
import { useLeagueStore } from 'stores/leagueStore';
import { storeToRefs } from 'pinia';
import { useResponsive } from 'src/composables/reponsive';

const { actions, leadText, subject, reset } = useActionBar();
const { activePlayer, isMeActivePlayer, statusNoun, leagueStatus } = storeToRefs(useLeagueStore());
const { isMobile } = useResponsive();

async function handleAction(action: any) {
  try {
    action.callback();
    if (action.autoReset) {
      reset();
    }
  } catch (e) {
    console.error(e);
  }
}
</script>

<style scoped lang="scss">
/* Keep width control here; Quasar doesn't ship border utilities */
.actionBar {
  width: min(100%, 600px);
}

/* Optional: slightly slimmer chip buttons in the action row */
.compact-btn {
  min-height: 32px;
  font-size: 0.75rem;
}
</style>

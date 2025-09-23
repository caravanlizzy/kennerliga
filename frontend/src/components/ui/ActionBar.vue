<template>
  <!-- full-width wrapper so we can center the inner bar -->
    <div class="column actionBar radius q-ma-md">
      <div
        v-if="activePlayer"
        class="row items-center justify-around status-line q-py-xs "
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

        <!-- Divider dot -->
        <q-icon name="circle" size="6px" class="text-grey-5" />

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

      <q-separator inset v-if="isMeActivePlayer"/>
      <div
        v-if="isMeActivePlayer"
        class="row justify-between no-wrap items-center q-py-md q-px-lg"
      >
        <div v-if="leadText" class="text-body2 text-primary">
          <component  :is="leadText" />
        </div>
        <div v-if="subject" class="text-body1 text-primary text-weight-bold ">
          <component :is="subject" />
        </div>

        <div class="row items-center no-wrap q-gutter-xs">
          <kenner-button
            v-for="a in actions"
            :key="a.name"
            outline
            :color="a.buttonVariant || 'primary'"
            class="compact-btn q-px-sm q-py-xs text-caption"
            @click="handleAction(a)"
          >
            <q-icon v-if="a.icon" :name="a.icon" size="16px" class="q-mr-xs" />
            <span class="btn-label">{{ a.name }}</span>
          </kenner-button>
        </div>

      </div>
    </div>
</template>

<!-- ActionBar.vue -->
<script setup lang="ts">
import { useActionBar } from 'src/composables/actionBar';
import KennerButton from 'components/base/KennerButton.vue';
import { useLeagueStore } from 'stores/leagueStore';
import { storeToRefs } from 'pinia';

const { actions, leadText, subject, reset } = useActionBar();
const { activePlayer, isMeActivePlayer, statusNoun, leagueStatus } = storeToRefs(useLeagueStore());

async function handleAction(action: any) {
  try {
    action.callback();
    if(action.autoReset){
      reset();
    }
  } catch (e) {
    console.error(e);
  }
}
</script>

<style scoped lang="scss">
.actionBar-wrap {
  width: 100%;
}

/* The "action area" — full width on mobile, constrained & centered on desktop */
.actionBar {
  border: 3px solid #cdcdcd;
  width: min(100%, 800px); /* cap width on large screens */
  margin-inline: auto; /* center horizontally */
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

.radius {
  border-radius: 9px;
}
</style>

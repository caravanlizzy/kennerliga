<template>
  <!-- full-width wrapper so we can center the inner bar -->
    <div class="column actionBar radius q-mb-md">
      <div
        v-if="activePlayer"
        class="row items-center justify-between status-line q-py-xs"
      >
        <!-- Centered block -->
        <div
          class="row items-center justify-center col text-subtitle1 text-weight-regular text-italic"
        >
          <span class="text-bold">
            <q-chip :class="activePlayer?.colorClass" text-color="white">{{
              activePlayer?.username
            }}</q-chip
            >'s turn
          </span>
        </div>
      </div>
      <q-separator inset v-if="isMeActivePlayer"/>
      <div
        v-if="isMeActivePlayer"
        class="row justify-between no-wrap items-center q-py-md q-px-lg"
      >
        <div class="text-body2 text-primary">
          <component v-if="description" :is="description" />
        </div>

        <div class="row items-center no-wrap q-gutter-sm">
          <kenner-button
            outline
            :color="a.buttonVariant || 'primary'"
            v-for="a in actions"
            :key="a.name"
            @click="handleAction(a)"
          >
            {{ a.name }}
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

const { actions, description, reset } = useActionBar();
const { activePlayer, isMeActivePlayer } = storeToRefs(useLeagueStore());

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

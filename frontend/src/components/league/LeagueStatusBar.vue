<template>
  <div
    v-if="activePlayer && turnAction"
    class="league-status-bar row items-center no-wrap"
    :class="{ 'league-status-bar--my-turn': isMeActivePlayer }"
  >
    <q-icon name="ads_click" size="20px" class="q-mr-sm" />
    <div>
      <div class="league-status-bar__label">Current turn</div>
      <div class="league-status-bar__message">
        <template v-if="isMeActivePlayer">Your turn to {{ turnAction }}</template>
        <template v-else>
          <strong>{{ activePlayer.profile_name || activePlayer.username }}</strong>
          's turn to {{ turnAction }}
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useMyLeagueStore } from 'src/composables/myLeague';

const { activePlayer, isMeActivePlayer, leagueStatus } = storeToRefs(useMyLeagueStore());

const turnAction = computed(() => {
  switch (leagueStatus.value) {
    case 'PICKING':
      return 'pick a game';
    case 'REPICKING':
      return 'pick again';
    case 'BANNING':
      return 'ban a game';
    default:
      return undefined;
  }
});
</script>

<style scoped lang="scss">
.league-status-bar {
  margin: 0 -24px;
  padding: 12px 24px;
  background: #eaf4ff;
  border-bottom: 1px solid #b9d8f5;
  color: #123b5d;

  &--my-turn {
    background: #fff3d9;
    border-color: #f0c66c;
    color: #5c3b00;
  }

  &__label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  &__message {
    font-size: 0.95rem;
    line-height: 1.25;
  }

  @media (max-width: 599px) {
    margin: 0 -16px;
    padding: 12px 16px;
  }
}
</style>

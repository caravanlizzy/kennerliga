<template>
  <div class="player-card">
    <!-- Colored Header -->
    <div class="card-header" :class="member.colorClass">
      <div class="row items-center text-weight-medium no-wrap">
        {{ member.username }}
        <div v-if="member.is_active_player" class="active-indicator q-ml-xs">
          <span class="dot" />
        </div>
      </div>

      <div class="row items-center q-gutter-xs no-wrap">
        <q-badge
          v-if="member.selected_game"
          class="badge neutral-badge"
        >
          <q-icon name="sports_esports" size="14px" class="q-mr-xs" />
          GAME
        </q-badge>

        <q-badge
          v-if="member.banned_game"
          class="badge neutral-badge"
        >
          <q-icon name="block" size="14px" class="q-mr-xs" />
          BAN
        </q-badge>
      </div>
    </div>

    <!-- Body -->
    <div class="card-body">
      <SelectedGameInfo
        :member="member"
        :isBannable="isBannable"
        :isBanning="isBanning"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import SelectedGameInfo from 'components/league/SelectedGameInfo.vue';
import { TLeagueMember } from 'src/types';
import { storeToRefs } from 'pinia';
import { useLeagueStore } from 'stores/leagueStore';

defineProps<{
  member: any;
}>();

const {leagueStatus, isMeActivePlayer } = storeToRefs(useLeagueStore());


function isBannable(member: TLeagueMember): boolean {
  // only bannable if leagueStatus is in banning phase
  if (leagueStatus.value !== 'BANNING') return false;

  // only bannable if *I* am the active player
  if (!isMeActivePlayer.value) return false;

  // I can ban others, but not myself
  return !member.is_active_player;
}

function isBanning(member: TLeagueMember): boolean {
  return leagueStatus.value === 'BANNING' && member.is_active_player;
}

</script>

<style scoped lang="scss">
.player-card {
  background: #f3f3f3;
  border-radius: 8px;
  overflow: hidden;
  //box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  border: 1px solid rgb(207, 207, 207);
}

.card-header {
  padding: 8px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
}

.card-body {
  padding: 12px;
  background: white;
}

.badge {
  font-size: 0.65rem;
  padding: 2px 8px;
  border-radius: 6px;
  display: flex;
  align-items: center;
}

.neutral-badge {
  background-color: rgba(255, 255, 255, 0.15);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  font-weight: 500;
}

.active-indicator {
  display: flex;
  align-items: center;
  margin-left: 7px;
}

.dot {
  height: 9px;
  width: 9px;
  border-radius: 50%;
  display: inline-block;
  background: white;
  animation: pulse 1.8s ease-in-out infinite;
}


@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.3);
    opacity: 0.5;
  }
}
</style>

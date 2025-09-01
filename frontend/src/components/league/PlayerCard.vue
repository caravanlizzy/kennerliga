<template>
  <q-card flat bordered class="q-ma-sm rounded-borders">
    <!-- Header -->
    <q-card-section
      class="row justify-between items-center text-white"
      :class="member.colorClass"
    >
      <!-- Username + active indicator -->
      <div class="row items-center no-wrap">
        <span class="text-subtitle2 text-weight-medium">
          {{ member.username }}
        </span>
        <q-badge
          v-if="member.is_active_player"
          rounded
          color="primary"
          text-color="white"
          class="q-ml-sm"
        >
          <q-icon name="circle" size="10px" class="q-mr-xs" />
          Active
        </q-badge>



      </div>

      <!-- Badges (Game / Ban) -->
      <div class="row items-center q-gutter-xs no-wrap">
        <q-badge v-if="member.selected_game" color="white" outline>
          <q-icon name="sports_esports" size="14px" class="q-mr-xs" />
          Game
        </q-badge>

        <q-badge v-if="member.banned_game" color="white" outline>
          <q-icon name="block" size="14px" class="q-mr-xs" />
          Ban
        </q-badge>
      </div>
    </q-card-section>

    <!-- Body -->
    <q-card-section class="q-pa-sm bg-grey-1">
      <SelectedGameInfo
        :member="member"
        :isBannable="isBannable"
        :isBanning="isBanning"
      />
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import SelectedGameInfo from 'components/league/SelectedGameInfo.vue';
import { TLeagueMember } from 'src/types';
import { storeToRefs } from 'pinia';
import { useLeagueStore } from 'stores/leagueStore';

defineProps<{ member: any }>();

const { leagueStatus, isMeActivePlayer } = storeToRefs(useLeagueStore());

function isBannable(member: TLeagueMember): boolean {
  return leagueStatus.value === 'BANNING' && isMeActivePlayer.value && !member.is_active_player;
}

function isBanning(member: TLeagueMember): boolean {
  return leagueStatus.value === 'BANNING' && member.is_active_player;
}
</script>

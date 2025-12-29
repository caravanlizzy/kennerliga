<template>
  <div class="row items-center no-wrap">
    <KennerButton
      v-if="isAuthenticated"
      :to="{ name: 'my-league' }"
      unelevated
      color="secondary"
      class="nav-item-radius text-weight-bold shadow-1"
      no-caps
    >
      <q-icon name="emoji_events" color="white" />
      <span v-show="!isMobile" class="q-ml-xs text-white">My League</span>
      <q-badge v-if="isMeActivePlayer" floating rounded color="positive" style="top: -4px; right: -4px; border: 2px solid white" />
    </KennerButton>
  </div>
</template>
<script setup lang="ts">
import { useResponsive } from 'src/composables/responsive';
import { storeToRefs } from 'pinia';
import { useLeagueStore } from 'stores/leagueStore';
import { useUserStore } from 'stores/userStore';
import KennerButton from 'components/base/KennerButton.vue';

const { isMobile } = useResponsive();
const { isAuthenticated, user } = storeToRefs(useUserStore());
const myLeagueStore = useLeagueStore(user.value?.myCurrentLeagueId)();
const { isMeActivePlayer } = storeToRefs(myLeagueStore);


</script>

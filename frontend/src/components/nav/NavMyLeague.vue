<template>
  <div class="row items-center no-wrap absolute-center">
    <q-btn
      v-if="isAuthenticated"
      :to="{ name: 'my-league' }"
      unelevated
      color="white"
      class="nav-item-radius text-weight-medium"
      no-caps
    >
      <q-icon color="amber-6" name="emoji_events" />
      <span v-show="!isMobile" class="q-ml-xs text-primary">My League</span>
      <q-badge v-if="isMeActivePlayer" floating rounded color="positive" />
    </q-btn>
  </div>
</template>
<script setup lang="ts">
import { useResponsive } from 'src/composables/reponsive';
import { storeToRefs } from 'pinia';
import { useLeagueStore } from 'stores/leagueStore';
import { useUserStore } from 'stores/userStore';

const { isMobile } = useResponsive();
const { isAuthenticated, user } = storeToRefs(useUserStore());
const myLeagueStore = useLeagueStore(user.value?.myCurrentLeagueId)();
const { isMeActivePlayer } = storeToRefs(myLeagueStore);


</script>

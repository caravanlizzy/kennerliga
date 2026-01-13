<template>
  <div class="row items-center no-wrap">
    <KennerButton
      v-if="isAuthenticated"
      :to="{ name: 'my-league' }"
      unelevated
      color="primary"
      class="league-btn text-weight-bold"
      :class="{ 'is-active': isMeActivePlayer }"
      no-caps
    >
      <q-icon name="ads_click" class="q-mr-xs" />
      <span v-show="!isMobile">My League</span>
      <q-badge v-if="isMeActivePlayer" floating rounded style="top: -6px; right: -6px; border: 2px solid white" color="warning" text-color="white" label="!" />
    </KennerButton>
  </div>
</template>
<script setup lang="ts">
import { useResponsive } from 'src/composables/responsive';
import { storeToRefs } from 'pinia';
import { useUserStore } from 'stores/userStore';
import KennerButton from 'components/base/KennerButton.vue';
import { computed } from 'vue';

const { isMobile } = useResponsive();
const { isAuthenticated, user } = storeToRefs(useUserStore());
const isMeActivePlayer = computed(() => user.value?.isMyTurn ?? false);


</script>

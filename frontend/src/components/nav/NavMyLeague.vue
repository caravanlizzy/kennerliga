<template>
  <div class="row items-center no-wrap">
    <KennerButton
      v-if="isAuthenticated"
      :to="{ name: 'my-league' }"
      unelevated
      color="primary"
      shape="squircle"
      class="league-btn text-weight-bold"
      :class="{ 'is-active': isMeActivePlayer }"
      style="height: 36px; min-width: 36px;"
      no-caps
    >
      <div class="row items-center no-wrap">
        <q-icon name="ads_click" color="secondary" :class="{ 'q-mr-xs': !isMobile }" />
        <span v-if="!isMobile">My League</span>
      </div>
      <q-badge v-if="isMeActivePlayer" floating rounded class="notification-dot" color="warning" />
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

<style scoped>
.notification-dot {
  width: 14px;
  height: 14px;
  min-height: 14px;
  padding: 0;
  top: -2px !important;
  right: -2px !important;
  border: 2px solid white;
  border-radius: 50% !important;
}
</style>

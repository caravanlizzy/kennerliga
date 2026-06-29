<template>
  <q-page class="column col q-pa-none">
    <HomeAnnouncements v-if="!isMobile" :is-mobile="isMobile" />

    <div class="q-mx-auto home-page-container" :class="[{ 'q-pa-md': !isMobile }, isMobile ? 'col column' : '']">
      <WelcomeSection
        v-if="showWelcome"
        :is-authenticated="isAuthenticated"
      />

      <AuthenticatedHomeDashboard
        v-if="isAuthenticated && !isMobile"
      />
    </div>
  </q-page>
</template>

<script setup lang="ts">
defineOptions({ name: 'IndexPage' });
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useUserStore } from 'stores/userStore';
import { useResponsive } from 'src/composables/responsive';
import HomeAnnouncements from 'components/home/HomeAnnouncements.vue';
import WelcomeSection from 'components/home/WelcomeSection.vue';
import AuthenticatedHomeDashboard from 'components/home/AuthenticatedHomeDashboard.vue';

const { isMobile } = useResponsive();
const { isAuthenticated } = storeToRefs(useUserStore());
const route = useRoute();

const showWelcome = computed(
  () => isMobile.value || route.name === 'home'
);
</script>

<style scoped>
.home-page-container {
  max-width: 1300px;
  width: 100%;
}

.home-page-container.col {
  flex: 1 1 auto;
  min-height: 0;
}

@media (min-width: 1024px) {
  .sticky-column {
    position: sticky;
  }
}
</style>

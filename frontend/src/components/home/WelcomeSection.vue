<template>
  <div :id="id" class="welcome-section-root">
    <template v-if="!isAuthenticated">
      <div
        class="column items-center justify-center relative-position q-mb-xl"
        :class="isMobile ? 'q-pa-lg' : 'q-pa-xl'"
      >
        <!-- Background Watermark -->
        <div
          class="absolute-top-right q-ma-lg"
          style="opacity: 0.04; pointer-events: none; transform: rotate(-15deg); z-index: 0"
        >
          <q-icon name="img:icons/favicon.svg" :size="isMobile ? '120px' : '200px'" />
        </div>

        <div class="full-width relative-position" style="z-index: 1">
          <!-- Hero Section -->
          <div class="column items-center text-center" :class="isMobile ? 'q-mb-lg' : 'q-mb-xl'">
            <q-icon name="img:icons/favicon.svg" :size="isMobile ? '80px' : '120px'" class="q-mb-lg" />
            <h1 :class="[isMobile ? 'text-h4' : 'text-h2', 'text-weight-bold q-my-none tracking-tighter']" style="letter-spacing: -2px; text-shadow: 0 2px 4px rgba(0,0,0,0.05)">
              <span class="text-primary">Kenner</span><span class="text-accent">Liga</span>
            </h1>
            <p :class="[isMobile ? 'text-subtitle1' : 'text-h5', 'text-grey-8 q-mt-md q-mb-xl']">
              A private space for our boardgame league. We manage everything from season registration and auto league assignment to game picking, banning, and results. Stay connected via community chat and keep an eye on past season stats and overviews.
            </p>
            <div class="row q-gutter-md justify-center">
              <KennerButton
                color="primary"
                label="Login"
                icon="login"
                to="/login"
                :size="isMobile ? 'md' : 'lg'"
              />
              <KennerButton
                color="secondary"
                outline
                label="Rules"
                icon="gavel"
                to="/rules"
                :size="isMobile ? 'md' : 'lg'"
              />
            </div>
          </div>

          <!-- Private Note -->
          <div :class="[isMobile ? 'q-mt-lg q-pa-md' : 'q-mt-xl q-pa-lg', 'text-center border-top-subtle']">
            <q-icon name="lock" size="xs" color="grey-6" class="q-mr-sm" />
            <span class="text-body2 text-grey-6">
              An account is required to view league details and participate.
            </span>
          </div>

          <ReleaseNotesSection :class="isMobile ? 'q-px-md' : 'q-px-lg'" />
        </div>
      </div>
    </template>
    <template v-else>
      <div
        class="relative-position"
        :class="[isMobile ? 'q-pa-none auth-mobile-wrap' : 'q-pa-none q-mb-md']"
      >
        <div class="relative-position" :class="isMobile ? 'auth-mobile-inner' : ''" style="z-index: 1">
          <q-card
            flat
            bordered
            class="combined-card q-pa-lg"
            :class="isMobile ? 'combined-card--mobile' : 'q-mt-xl'"
          >
            <div :class="isMobile ? '' : 'row q-col-gutter-lg items-start'">
              <div :class="isMobile ? '' : 'col-12 col-md-6'">
                <PurposeSection />
              </div>
              <div :class="isMobile ? 'q-mt-md combined-divider-mobile q-pt-md' : 'col-12 col-md-6 combined-divider-desktop'">
                <ReleaseNotesSection />
              </div>
            </div>
          </q-card>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import ReleaseNotesSection from 'components/home/ReleaseNotesSection.vue';
import PurposeSection from 'components/home/PurposeSection.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { useResponsive } from 'src/composables/responsive';
import { onMounted, onUnmounted } from 'vue';

withDefaults(
  defineProps<{
    isAuthenticated: boolean;
    id?: string;
  }>(),
  {
    id: 'welcome'
  }
);

const { isMobile } = useResponsive();

onMounted(() => {
  // Navigation registration removed
});

onUnmounted(() => {
  // Navigation registration removed
});
</script>

<style scoped lang="scss">
.fancy-close-btn {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  opacity: 0.8;
  background: rgba(0, 0, 0, 0.05);
  color: var(--q-primary);
  font-weight: bold;

  &:hover {
    opacity: 1;
    background: rgba(0, 0, 0, 0.12);
    transform: rotate(90deg) scale(1.15);
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
  }
}

.border-top-subtle {
  border-top: 1px solid rgba(54, 64, 88, 0.08);
}

.welcome-section-root {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  min-height: 0;
}

.auth-mobile-wrap {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  min-height: 0;
}

.auth-mobile-inner {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  min-height: 0;
}

.combined-card {
  border-radius: 9px;
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.combined-card--mobile {
  margin: 0;
  border-left: none;
  border-right: none;
  border-radius: 0;
  box-shadow: none;
}

.combined-divider-mobile {
  border-top: 1px solid rgba(54, 64, 88, 0.08);
}

.combined-divider-desktop {
  position: relative;
}

@media (min-width: 1024px) {
  .combined-divider-desktop::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 1px;
    background: rgba(54, 64, 88, 0.08);
  }
}
</style>

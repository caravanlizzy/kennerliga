<template>
  <div :id="id">
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
        </div>
      </div>
    </template>
    <template v-else>
      <div
        class="relative-position q-mb-md"
        :class="isMobile ? 'q-pa-md' : 'q-px-lg q-pt-md q-pb-none'"
      >
        <div class="relative-position" style="z-index: 1">
          <div
            :class="[isMobile ? 'text-h5' : 'text-h4', 'text-weight-bold text-dark tracking-tighter']"
            style="letter-spacing: -1px;"
          >
            Welcome back!
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
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
</style>

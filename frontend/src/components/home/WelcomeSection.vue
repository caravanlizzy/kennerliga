<template>
  <div v-if="!isMinimized">
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

        <q-btn
          v-if="!isMobile"
          flat
          round
          dense
          icon="close"
          size="sm"
          class="absolute-top-right q-ma-xs fancy-close-btn"
          color="grey-7"
          @click="minimize"
          style="z-index: 2"
        >
          <q-tooltip>Close Welcome</q-tooltip>
        </q-btn>
        <div class="full-width relative-position" style="z-index: 1">
          <!-- Hero Section -->
          <div class="column items-center text-center" :class="isMobile ? 'q-mb-lg' : 'q-mb-xl'">
            <q-icon name="img:icons/favicon.svg" :size="isMobile ? '80px' : '120px'" class="q-mb-lg" />
            <h1 :class="[isMobile ? 'text-h4' : 'text-h2', 'text-weight-bold q-my-none text-dark tracking-tighter']" style="letter-spacing: -2px; text-shadow: 0 2px 4px rgba(0,0,0,0.05)">
              Kenner<span class="text-primary">Liga</span>
            </h1>
            <p :class="[isMobile ? 'text-subtitle1' : 'text-h5', 'text-grey-8 q-mt-md q-mb-xl']">
              Welcome to KennerLiga! This is your go-to spot for following the league, signing up, picking your games, and logging your wins. Once the dust settles, we've got all the stats and data ready for you to dive into.
            </p>
            <div class="row q-gutter-md justify-center">
              <KennerButton
                outline
                color="dark"
                label="Sign In"
                icon="login"
                to="/login"
                :size="isMobile ? 'md' : 'lg'"
              />
            </div>
          </div>

          <!-- Features Section -->
          <div class="row q-col-gutter-xl" :class="isMobile ? 'q-pt-lg' : 'q-pt-xl'">
            <div class="col-12 col-md-4">
              <div class="column items-center text-center">
                <q-avatar :size="isMobile ? '50px' : '70px'" :font-size="isMobile ? '24px' : '36px'" color="primary-1" text-color="primary" icon="history" />
                <h3 :class="[isMobile ? 'text-h6' : 'text-h5', 'text-weight-bold q-my-md']">Seasonal Play</h3>
                <p class="text-body1 text-grey-7">
                  Organize your gaming year into competitive seasons with custom scoring and rankings.
                </p>
              </div>
            </div>
            <div class="col-12 col-md-4">
              <div class="column items-center text-center">
                <q-avatar :size="isMobile ? '50px' : '70px'" :font-size="isMobile ? '24px' : '36px'" color="accent-1" text-color="accent" icon="leaderboard" />
                <h3 :class="[isMobile ? 'text-h6' : 'text-h5', 'text-weight-bold q-my-md']">Live Standings</h3>
                <p class="text-body1 text-grey-7">
                  Stay updated with real-time leaderboards and detailed performance statistics for every player.
                </p>
              </div>
            </div>
            <div class="col-12 col-md-4">
              <div class="column items-center text-center">
                <q-avatar :size="isMobile ? '50px' : '70px'" :font-size="isMobile ? '24px' : '36px'" color="secondary-1" text-color="secondary" icon="chat" />
                <h3 :class="[isMobile ? 'text-h6' : 'text-h5', 'text-weight-bold q-my-md']">Community Chat</h3>
                <p class="text-body1 text-grey-7">
                  Discuss strategies, schedule game nights, and share your victories with fellow Kenner.
                </p>
              </div>
            </div>
          </div>

          <!-- Private Note -->
          <div :class="[isMobile ? 'q-mt-lg q-pa-md' : 'q-mt-xl q-pa-lg', 'text-center border-top-subtle']">
            <q-icon name="lock" size="xs" color="grey-6" class="q-mr-sm" />
            <span class="text-body2 text-grey-6">
              KennerLiga is a private platform. Registration is required to view full league details and participate.
            </span>
          </div>
        </div>
      </div>
    </template>
    <template v-else>
      <div
        class="relative-position q-mb-xl"
        :class="isMobile ? 'q-pa-md' : 'q-px-lg q-pt-lg q-pb-lg'"
      >
        <!-- Background Watermark -->
        <div
          class="absolute-top-right q-ma-md"
          style="opacity: 0.04; pointer-events: none; transform: rotate(-15deg); z-index: 0"
        >
          <q-icon name="img:icons/favicon.svg" :size="isMobile ? '100px' : '140px'" />
        </div>

        <q-btn
          v-if="!isMobile"
          flat
          round
          dense
          icon="close"
          size="sm"
          class="absolute-top-right q-ma-xs fancy-close-btn"
          color="grey-7"
          @click="minimize"
          style="z-index: 2"
        >
          <q-tooltip>Close Welcome</q-tooltip>
        </q-btn>
        <div class="relative-position" style="z-index: 1">
          <div :class="[isMobile ? 'text-h5' : 'text-h4', 'text-weight-bold text-dark tracking-tight']" style="letter-spacing: -0.5px; text-shadow: 0 1px 2px rgba(0,0,0,0.05)">Welcome back!</div>
          <div :class="[isMobile ? 'text-body1' : 'text-subtitle1', 'text-grey-8 q-mt-sm']" style="opacity: 0.9">
            Glad to have you here! This is your central hub for everything KennerLiga. Here's a quick rundown of what you'll find:
            <div class="row q-col-gutter-md q-mt-xs text-body1">
              <div class="col-12 col-sm-6">
                <div class="row no-wrap items-center">
                  <q-icon name="sensors" color="accent" size="xs" class="q-mr-xs" />
                  <span class="text-weight-bold q-mr-xs">Live Action:</span> See what's happening right now across the leagues.
                </div>
                <div class="row no-wrap items-center q-mt-xs">
                  <q-icon name="history" color="primary" size="xs" class="q-mr-xs" />
                  <span class="text-weight-bold q-mr-xs">Seasons:</span> Check current standings and dive into past season data.
                </div>
              </div>ir
              <div class="col-12 col-sm-6">
                <div class="row no-wrap items-center">
                  <q-icon name="leaderboard" color="primary" size="xs" class="q-mr-xs" />
                  <span class="text-weight-bold q-mr-xs">Leaderboard:</span> See the overall rankings and who's leading this year.
                </div>
                <div class="row no-wrap items-center q-mt-xs">
                  <q-icon name="chat" color="primary" size="xs" class="q-mr-xs" />
                  <span class="text-weight-bold q-mr-xs">Kennerchat:</span> Catch up with the community and plan your next session.
                </div>
              </div>
            </div>
            <div class="q-mt-md text-body2 text-grey-7">
              <q-icon name="info" size="xs" class="q-mr-xs" />
              Everything is tracked, so you can check out the stats and see how you're doing later on.
              <span v-if="!isMobile">Feel free to close any windows you don't need – they'll stay tucked away in the navbar icons if you want them back.</span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import KennerButton from 'components/base/KennerButton.vue';
import { useUiStore } from 'src/stores/uiStore';
import { useResponsive } from 'src/composables/responsive';
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    isAuthenticated: boolean;
    id?: string;
  }>(),
  {
    id: 'welcome'
  }
);

const uiStore = useUiStore();
const { isMobile } = useResponsive();
const isMinimized = computed(() => !isMobile && uiStore.isMinimized(props.id));

function minimize() {
  uiStore.minimize({
    id: props.id,
    title: 'Welcome',
    icon: 'auto_awesome',
    color: 'primary',
    type: 'section'
  });
}
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

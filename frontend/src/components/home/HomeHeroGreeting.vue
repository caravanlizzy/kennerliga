<template>
  <div class="home-hero-greeting q-pa-md q-mb-md">
    <div class="row items-center justify-between q-col-gutter-sm">
      <!-- Left: Player Identity & League Status -->
      <div class="col-12 col-md-6 row items-center no-wrap">
        <UserAvatar
          v-if="user"
          :display-username="displayName"
          :shape="user.avatar_shape"
          :color="user.avatar_color"
          size="42px"
          class="q-mr-md flex-shrink-0"
        />
        <div class="column justify-center min-width-0">
          <div class="row items-center no-wrap q-gutter-x-sm">
            <span class="text-subtitle1 text-weight-bold ellipsis text-strong">
              Welcome back, {{ greetingName }}
            </span>
            <span
              v-if="isMyTurn"
              class="turn-alert-badge row items-center no-wrap q-px-xs q-py-none"
            >
              <span class="pulse-dot q-mr-xs" />
              Your turn
            </span>
          </div>
          <div class="text-caption text-muted ellipsis">
            <span v-if="seasonStatusText">{{ seasonStatusText }}</span>
            <span v-else>Board Game League Overview</span>
          </div>
        </div>
      </div>

      <!-- Right: Direct Utility Action Chips & Subtitle -->
      <div
        class="col-12 col-md-6 column items-start items-md-end justify-center hero-action-section q-mt-xs q-mt-md-none"
      >
        <div class="text-caption text-muted hero-action-subtitle q-mb-xs">
          Statistics &amp; Quick Access
        </div>
        <div
          class="row items-center justify-start justify-md-end q-gutter-xs flex-wrap hero-action-group"
        >
          <KennerButton
            v-if="hasMyLeague"
            icon="emoji_events"
            label="My League"
            size="sm"
            class="hero-fancy-btn hero-fancy-btn--league"
            :to="{ name: 'my-league' }"
          />
          <KennerButton
            icon="stars"
            label="Hall of Fame"
            size="sm"
            class="hero-fancy-btn hero-fancy-btn--hof"
            :to="{ name: 'statistics' }"
          />
          <KennerButton
            icon="people_alt"
            label="Players"
            size="sm"
            class="hero-fancy-btn hero-fancy-btn--players"
            :to="{ name: 'players' }"
          />
          <KennerButton
            icon="sports_esports"
            label="Games"
            size="sm"
            class="hero-fancy-btn hero-fancy-btn--games"
            :to="{ name: 'games' }"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'HomeHeroGreeting' });
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useUserStore } from 'stores/userStore';
import { useHomeSeasonStore } from 'stores/homeSeasonStore';
import UserAvatar from 'components/ui/UserAvatar.vue';
import KennerButton from 'components/base/KennerButton.vue';

const userStore = useUserStore();
const homeSeasonStore = useHomeSeasonStore();

const { user } = storeToRefs(userStore);
const { selectedSeason } = storeToRefs(homeSeasonStore);

const displayName = computed(() => user.value?.username ?? 'Player');
const greetingName = computed(
  () => user.value?.first_name || user.value?.username || 'Player'
);
const hasMyLeague = computed(() => Boolean(user.value?.myCurrentLeagueId));
const isMyTurn = computed(() => Boolean(user.value?.isMyTurn));

const seasonStatusText = computed(() => {
  const season = selectedSeason.value;
  if (!season) return '';
  const monthName = new Date(season.year, season.month - 1).toLocaleString(
    'default',
    { month: 'long' }
  );
  if (season.status === 'RUNNING') {
    return `${monthName} ${season.year} Season in progress`;
  }
  if (season.status === 'UPCOMING') {
    return `${monthName} ${season.year} Season is upcoming`;
  }
  return `${monthName} ${season.year} Season concluded`;
});
</script>

<style scoped lang="scss">
.home-hero-greeting {
  background: var(--kenner-card-bg);
  border: 1px solid var(--kenner-border-subtle);
  border-radius: var(--kenner-card-radius);
  box-shadow: var(--kenner-card-shadow);
  transition: all 0.2s ease;
}

.text-strong {
  color: var(--kenner-text-strong);
}

.text-muted {
  color: var(--kenner-text-muted);
}

.min-width-0 {
  min-width: 0;
}

.flex-shrink-0 {
  flex-shrink: 0;
}

.turn-alert-badge {
  background: rgba(245, 158, 11, 0.12);
  color: #d97706;
  font-size: 11px;
  font-weight: 700;
  border-radius: 9999px;
  padding: 1px 8px;
  letter-spacing: 0.3px;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #d97706;
  display: inline-block;
  animation: pulse-ring 1.8s cubic-bezier(0.455, 0.03, 0.515, 0.955) infinite;
}

.hero-action-subtitle {
  font-size: 11.5px;
  font-weight: 600;
  letter-spacing: 0.3px;
  color: var(--kenner-text-muted);
}

.hero-fancy-btn {
  position: relative;
  overflow: hidden;
  font-weight: 600;
  font-size: 12.5px;
  letter-spacing: 0.25px;
  border-radius: var(--kenner-card-radius, 12px) !important;
  padding: 4px 12px !important;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);

  :deep(.q-icon) {
    font-size: 16px;
    margin-right: 4px;
    transition: transform 0.2s ease, color 0.2s ease;
  }

  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: -120%;
    width: 60%;
    height: 100%;
    background: linear-gradient(
      90deg,
      transparent 0%,
      rgba(255, 255, 255, 0.25) 50%,
      transparent 100%
    );
    transform: skewX(-20deg);
    pointer-events: none;
    transition: none;
  }

  &:hover {
    transform: translateY(-1px);

    &::after {
      left: 140%;
      transition: left 0.65s ease-in-out;
    }

    :deep(.q-icon) {
      transform: scale(1.1);
    }
  }

  &:active {
    transform: translateY(0);
  }
}

.hero-fancy-btn--league {
  background: linear-gradient(
    135deg,
    rgba(245, 158, 11, 0.12) 0%,
    rgba(217, 119, 6, 0.06) 100%
  ) !important;
  color: var(--kenner-gold-text, #b45309) !important;
  border: 1px solid var(--kenner-gold-border, rgba(245, 158, 11, 0.3)) !important;
  box-shadow: 0 1px 3px rgba(245, 158, 11, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);

  :deep(.q-icon) {
    color: #d97706;
  }

  &:hover {
    background: linear-gradient(
      135deg,
      rgba(245, 158, 11, 0.2) 0%,
      rgba(217, 119, 6, 0.12) 100%
    ) !important;
    border-color: rgba(245, 158, 11, 0.55) !important;
    color: #78350f !important;
    box-shadow: 0 3px 10px rgba(245, 158, 11, 0.2),
      inset 0 1px 0 rgba(255, 255, 255, 0.8);

    :deep(.q-icon) {
      color: #b45309;
    }
  }
}

.hero-fancy-btn--hof {
  background: linear-gradient(
    135deg,
    rgba(139, 92, 246, 0.1) 0%,
    rgba(124, 58, 237, 0.05) 100%
  ) !important;
  color: var(--kenner-accent-text, #5e35b1) !important;
  border: 1px solid rgba(139, 92, 246, 0.28) !important;
  box-shadow: 0 1px 3px rgba(139, 92, 246, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);

  :deep(.q-icon) {
    color: #7c3aed;
  }

  &:hover {
    background: linear-gradient(
      135deg,
      rgba(139, 92, 246, 0.18) 0%,
      rgba(124, 58, 237, 0.1) 100%
    ) !important;
    border-color: rgba(139, 92, 246, 0.5) !important;
    color: #5b21b6 !important;
    box-shadow: 0 3px 10px rgba(139, 92, 246, 0.2),
      inset 0 1px 0 rgba(255, 255, 255, 0.8);

    :deep(.q-icon) {
      color: #6d28d9;
    }
  }
}

.hero-fancy-btn--players {
  background: linear-gradient(
    135deg,
    rgba(2, 132, 199, 0.08) 0%,
    rgba(3, 105, 161, 0.04) 100%
  ) !important;
  color: #0369a1 !important;
  border: 1px solid rgba(2, 132, 199, 0.25) !important;
  box-shadow: 0 1px 3px rgba(2, 132, 199, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);

  :deep(.q-icon) {
    color: #0284c7;
  }

  &:hover {
    background: linear-gradient(
      135deg,
      rgba(2, 132, 199, 0.16) 0%,
      rgba(3, 105, 161, 0.08) 100%
    ) !important;
    border-color: rgba(2, 132, 199, 0.45) !important;
    color: #075985 !important;
    box-shadow: 0 3px 10px rgba(2, 132, 199, 0.18),
      inset 0 1px 0 rgba(255, 255, 255, 0.8);

    :deep(.q-icon) {
      color: #0369a1;
    }
  }
}

.hero-fancy-btn--games {
  background: linear-gradient(
    135deg,
    rgba(16, 185, 129, 0.08) 0%,
    rgba(5, 150, 105, 0.04) 100%
  ) !important;
  color: var(--kenner-success-text, #15803d) !important;
  border: 1px solid rgba(16, 185, 129, 0.25) !important;
  box-shadow: 0 1px 3px rgba(16, 185, 129, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);

  :deep(.q-icon) {
    color: #059669;
  }

  &:hover {
    background: linear-gradient(
      135deg,
      rgba(16, 185, 129, 0.16) 0%,
      rgba(5, 150, 105, 0.08) 100%
    ) !important;
    border-color: rgba(16, 185, 129, 0.45) !important;
    color: #065f46 !important;
    box-shadow: 0 3px 10px rgba(16, 185, 129, 0.18),
      inset 0 1px 0 rgba(255, 255, 255, 0.8);

    :deep(.q-icon) {
      color: #047857;
    }
  }
}

.body--dark {
  .hero-fancy-btn {
    &::after {
      background: linear-gradient(
        90deg,
        transparent 0%,
        rgba(255, 255, 255, 0.12) 50%,
        transparent 100%
      );
    }
  }

  .hero-fancy-btn--league {
    background: linear-gradient(
      135deg,
      rgba(245, 158, 11, 0.18) 0%,
      rgba(180, 83, 9, 0.1) 100%
    ) !important;
    color: var(--kenner-gold-text, #fbbf24) !important;
    border-color: var(--kenner-gold-border, rgba(245, 158, 11, 0.35)) !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25),
      inset 0 1px 0 rgba(255, 255, 255, 0.12);

    :deep(.q-icon) {
      color: #fbbf24;
    }

    &:hover {
      background: linear-gradient(
        135deg,
        rgba(245, 158, 11, 0.28) 0%,
        rgba(180, 83, 9, 0.18) 100%
      ) !important;
      border-color: rgba(245, 158, 11, 0.7) !important;
      color: #ffffff !important;
      box-shadow: 0 4px 14px rgba(245, 158, 11, 0.35),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);

      :deep(.q-icon) {
        color: #fef08a;
      }
    }
  }

  .hero-fancy-btn--hof {
    background: linear-gradient(
      135deg,
      rgba(139, 92, 246, 0.16) 0%,
      rgba(109, 40, 217, 0.1) 100%
    ) !important;
    color: var(--kenner-accent-text, #b39ddb) !important;
    border-color: rgba(139, 92, 246, 0.35) !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25),
      inset 0 1px 0 rgba(255, 255, 255, 0.12);

    :deep(.q-icon) {
      color: #c084fc;
    }

    &:hover {
      background: linear-gradient(
        135deg,
        rgba(139, 92, 246, 0.26) 0%,
        rgba(109, 40, 217, 0.16) 100%
      ) !important;
      border-color: rgba(139, 92, 246, 0.65) !important;
      color: #ffffff !important;
      box-shadow: 0 4px 14px rgba(139, 92, 246, 0.32),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);

      :deep(.q-icon) {
        color: #f3e8ff;
      }
    }
  }

  .hero-fancy-btn--players {
    background: linear-gradient(
      135deg,
      rgba(2, 132, 199, 0.16) 0%,
      rgba(3, 105, 161, 0.1) 100%
    ) !important;
    color: var(--kenner-info-text, #60a5fa) !important;
    border-color: rgba(2, 132, 199, 0.35) !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25),
      inset 0 1px 0 rgba(255, 255, 255, 0.12);

    :deep(.q-icon) {
      color: #38bdf8;
    }

    &:hover {
      background: linear-gradient(
        135deg,
        rgba(2, 132, 199, 0.26) 0%,
        rgba(3, 105, 161, 0.16) 100%
      ) !important;
      border-color: rgba(2, 132, 199, 0.65) !important;
      color: #ffffff !important;
      box-shadow: 0 4px 14px rgba(2, 132, 199, 0.32),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);

      :deep(.q-icon) {
        color: #e0f2fe;
      }
    }
  }

  .hero-fancy-btn--games {
    background: linear-gradient(
      135deg,
      rgba(16, 185, 129, 0.16) 0%,
      rgba(5, 150, 105, 0.1) 100%
    ) !important;
    color: var(--kenner-success-text, #4ade80) !important;
    border-color: rgba(16, 185, 129, 0.35) !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25),
      inset 0 1px 0 rgba(255, 255, 255, 0.12);

    :deep(.q-icon) {
      color: #34d399;
    }

    &:hover {
      background: linear-gradient(
        135deg,
        rgba(16, 185, 129, 0.26) 0%,
        rgba(5, 150, 105, 0.16) 100%
      ) !important;
      border-color: rgba(16, 185, 129, 0.65) !important;
      color: #ffffff !important;
      box-shadow: 0 4px 14px rgba(16, 185, 129, 0.32),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);

      :deep(.q-icon) {
        color: #d1fae5;
      }
    }
  }
}

@keyframes pulse-ring {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.7);
  }
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 5px rgba(245, 158, 11, 0);
  }
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(245, 158, 11, 0);
  }
}
</style>

<template>
  <div class="home-hero-greeting q-pa-md q-mb-md">
    <div class="row items-center justify-between q-col-gutter-sm">
      <!-- Left: Player Identity & League Status -->
      <div class="col-12 col-md-7 row items-center no-wrap">
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

      <!-- Right: Direct Utility Action Chips -->
      <div
        class="col-12 col-md-5 row items-center justify-end q-gutter-xs flex-wrap"
      >
        <KennerButton
          v-if="hasMyLeague"
          outline
          color="primary"
          icon="emoji_events"
          label="My League"
          size="sm"
          :to="{ name: 'my-league' }"
        />
        <KennerButton
          flat
          color="primary"
          icon="stars"
          label="Hall of Fame"
          size="sm"
          :to="{ name: 'statistics' }"
        />
        <KennerButton
          flat
          color="primary"
          icon="people_alt"
          label="Players"
          size="sm"
          :to="{ name: 'players' }"
        />
        <KennerButton
          flat
          color="primary"
          icon="sports_esports"
          label="Games"
          size="sm"
          :to="{ name: 'games' }"
        />
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

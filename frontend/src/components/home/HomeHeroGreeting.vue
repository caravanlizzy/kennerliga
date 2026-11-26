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

      <!-- Right: Main navigation -->
      <div
        class="col-12 col-md-6 column items-start items-md-end justify-center hero-action-section q-mt-xs q-mt-md-none"
      >
        <div class="text-caption text-muted hero-action-subtitle q-mb-sm">
          Explore Kennerliga
        </div>
        <nav class="hero-navigation" aria-label="Explore Kennerliga">
          <RouterLink
            v-if="hasMyLeague"
            class="hero-navigation-link hero-navigation-link--league"
            :to="{ name: 'my-league' }"
          >
            <q-icon
              name="emoji_events"
              class="hero-navigation-icon"
              aria-hidden="true"
            />
            <span class="hero-navigation-copy">
              <span class="hero-navigation-title">My League</span>
              <span class="hero-navigation-description">Your season</span>
            </span>
            <q-icon
              name="arrow_forward"
              class="hero-navigation-arrow"
              aria-hidden="true"
            />
          </RouterLink>
          <RouterLink
            class="hero-navigation-link hero-navigation-link--hof"
            :to="{ name: 'statistics' }"
          >
            <q-icon
              name="stars"
              class="hero-navigation-icon"
              aria-hidden="true"
            />
            <span class="hero-navigation-copy">
              <span class="hero-navigation-title">Hall of Fame</span>
              <span class="hero-navigation-description">All-time greats</span>
            </span>
            <q-icon
              name="arrow_forward"
              class="hero-navigation-arrow"
              aria-hidden="true"
            />
          </RouterLink>
          <RouterLink
            class="hero-navigation-link hero-navigation-link--players"
            :to="{ name: 'players' }"
          >
            <q-icon
              name="people_alt"
              class="hero-navigation-icon"
              aria-hidden="true"
            />
            <span class="hero-navigation-copy">
              <span class="hero-navigation-title">Players</span>
              <span class="hero-navigation-description">Skill &amp; stats</span>
            </span>
            <q-icon
              name="arrow_forward"
              class="hero-navigation-arrow"
              aria-hidden="true"
            />
          </RouterLink>
          <RouterLink
            class="hero-navigation-link hero-navigation-link--games"
            :to="{ name: 'games' }"
          >
            <q-icon
              name="sports_esports"
              class="hero-navigation-icon"
              aria-hidden="true"
            />
            <span class="hero-navigation-copy">
              <span class="hero-navigation-title">Games</span>
              <span class="hero-navigation-description"
                >Matches &amp; stats</span
              >
            </span>
            <q-icon
              name="arrow_forward"
              class="hero-navigation-arrow"
              aria-hidden="true"
            />
          </RouterLink>
        </nav>
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

.hero-navigation {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  width: 100%;
}

.hero-navigation-link {
  --hero-link-accent: var(--kenner-info-text, #0369a1);

  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 8px;
  min-width: 0;
  min-height: 64px;
  padding: 8px 10px;
  border-inline-start: 2px solid var(--hero-link-accent);
  border-bottom: 1px solid var(--kenner-border-subtle);
  color: var(--kenner-text-strong);
  text-decoration: none;
  transition: background-color 0.12s ease;

  &:hover {
    background-color: var(--kenner-border-subtle);
  }

  &:focus-visible {
    outline: 2px solid var(--hero-link-accent);
    outline-offset: -2px;
  }
}

.hero-navigation-link--league {
  --hero-link-accent: var(--kenner-gold-text, #b45309);
}

.hero-navigation-link--hof {
  --hero-link-accent: var(--kenner-accent-text, #5e35b1);
}

.hero-navigation-link--games {
  --hero-link-accent: var(--kenner-success-text, #15803d);
}

.hero-navigation-icon {
  color: var(--hero-link-accent);
  font-size: 20px;
}

.hero-navigation-copy {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.hero-navigation-title,
.hero-navigation-description {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hero-navigation-title {
  font-size: 12px;
  font-weight: 700;
  line-height: 1.3;
}

.hero-navigation-description {
  color: var(--kenner-text-muted);
  font-size: 10px;
  line-height: 1.4;
}

.hero-navigation-arrow {
  color: var(--hero-link-accent);
  font-size: 16px;
}

@media (max-width: 1023px) {
  .hero-navigation {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 420px) {
  .hero-navigation {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>

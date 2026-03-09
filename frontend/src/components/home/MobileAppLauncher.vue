<template>
  <div class="launcher-grid q-pt-md">
    <template v-for="tile in tiles" :key="tile.title">
      <div
        v-if="tile.visible"
        v-ripple
        class="launcher-item column items-center justify-center cursor-pointer relative-position overflow-hidden"
        :class="`bg-${tile.color}-soft`"
        @click="navigateTo(tile.route)"
      >
        <div class="tile-content column items-center">
          <q-icon
            :name="tile.icon"
            :color="tile.color"
            size="32px"
            class="q-mb-xs"
          />
          <div class="text-subtitle2 text-weight-medium text-center text-dark title-text">
            {{ tile.title }}
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useUserStore } from 'src/stores/userStore';
import { computed } from 'vue';

const router = useRouter();
const userStore = useUserStore();

const tiles = computed(() => [
  {
    title: 'My League',
    icon: 'ads_click',
    color: 'secondary',
    route: { name: 'my-league' },
    visible: !!userStore.user?.myCurrentLeagueId,
  },
  {
    title: 'Seasons',
    icon: 'military_tech',
    color: 'blue',
    route: { name: 'mobile-seasons' },
    visible: true,
  },
  {
    title: 'Leaderboard',
    icon: 'stars',
    color: 'orange',
    route: { name: 'mobile-leaderboard' },
    visible: true,
  },
  {
    title: 'Live',
    icon: 'bolt',
    color: 'deep-purple',
    route: { name: 'mobile-live' },
    visible: true,
  },
  {
    title: 'Chat',
    icon: 'chat',
    color: 'pink',
    route: { name: 'mobile-chat' },
    visible: true,
  },
]);

function navigateTo(route: any) {
  router.push(route);
}
</script>

<style scoped lang="scss">
.launcher-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 12px;
}

.launcher-item {
  height: 110px;
  border-radius: 16px;
  transition: transform 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
  border: none;

  &:active {
    transform: scale(0.96);
  }

  .title-text {
    font-size: 0.9rem;
    letter-spacing: 0.01em;
    opacity: 0.85;
  }
}

// Minimal background colors for a clean grid look
.bg-secondary-soft { background: #effcfc; }
.bg-blue-soft { background: #eff6ff; }
.bg-orange-soft { background: #fff8f0; }
.bg-deep-purple-soft { background: #f6f2ff; }
.bg-pink-soft { background: #fdf2f8; }

@media (min-width: 600px) {
  .launcher-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>

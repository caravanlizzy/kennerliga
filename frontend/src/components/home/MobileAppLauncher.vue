<template>
  <div class="launcher-container">
    <template v-for="(tile, idx) in visibleTiles" :key="tile.title">
      <div
        v-ripple
        class="launcher-row"
        @click="navigateTo(tile.route)"
      >
        <div class="row no-wrap items-center q-px-md q-py-md">
          <div class="row-icon-box flex flex-center">
            <q-icon :name="tile.icon" size="36px" class="row-icon" />
          </div>

          <div class="col q-ml-md">
            <div class="row-title">{{ tile.title }}</div>
            <div class="row-description">{{ tile.description }}</div>
          </div>
        </div>
        <q-separator v-if="idx < visibleTiles.length - 1" class="row-divider" />
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
    description: 'Pick, post and see standings',
    icon: 'ads_click',
    route: { name: 'my-league' },
    visible: !!userStore.user?.myCurrentLeagueId,
  },
  {
    title: 'Seasons',
    description: 'Browse past and current seasons',
    icon: 'military_tech',
    route: { name: 'seasons' },
    visible: true,
  },
  {
    title: 'Leaderboard',
    description: 'Check who is currently on top',
    icon: 'stars',
    route: { name: 'leaderboard' },
    visible: true,
  },
  {
    title: 'Live',
    description: 'Get info about what is going on in the leagues',
    icon: 'bolt',
    route: { name: 'live' },
    visible: true,
  },
  {
    title: 'Chat',
    description: 'Connect with other league members',
    icon: 'chat',
    route: { name: 'chat' },
    visible: true,
  },
]);

const visibleTiles = computed(() => tiles.value.filter(t => t.visible));

function navigateTo(route: Record<string, unknown>) {
  router.push(route as any);
}
</script>

<style scoped lang="scss">
.launcher-container {
  width: 100%;
  background: #faf8f5;
  display: flex;
  flex-direction: column;
  min-height: 100%;
  flex: 1 1 auto;
}

.launcher-row {
  position: relative;
  cursor: pointer;
  transition: background-color 0.2s ease;
  flex: 1 1 0;
  display: flex;
  flex-direction: column;
  justify-content: center;

  > .row {
    flex: 1 1 auto;
  }

  &:hover {
    background-color: rgba(0, 0, 0, 0.03);
  }

  &:active {
    background-color: rgba(0, 0, 0, 0.05);
  }
}

.row-icon-box {
  width: 48px;
  height: 48px;
  flex-shrink: 0;
}

.row-icon {
  color: #607d8b;
}

.row-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1a1a1a;
  letter-spacing: -0.2px;
  line-height: 1.25;
}

.row-description {
  font-size: 0.9rem;
  color: #78909c;
  line-height: 1.3;
  margin-top: 4px;
}

.row-divider {
  background-color: rgba(0, 0, 0, 0.06);
}
</style>

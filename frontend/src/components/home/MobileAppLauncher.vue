<template>
  <div class="launcher-grid q-pt-md">
    <template v-for="tile in tiles" :key="tile.title">
      <div v-if="tile.visible" class="launcher-item">
        <q-card
          flat
          v-ripple
          class="launcher-tile column items-center justify-center cursor-pointer relative-position overflow-hidden"
          @click="navigateTo(tile.route)"
        >
          <q-icon
            :name="tile.icon"
            :color="tile.color"
            size="28px"
            class="q-mb-xs"
          />
          <div class="text-caption text-weight-bold text-center text-dark">
            {{ tile.title }}
          </div>
        </q-card>
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
    color: 'primary',
    route: { name: 'my-league' },
    visible: !!userStore.user?.myCurrentLeagueId,
  },
  {
    title: 'Seasons',
    icon: 'military_tech',
    color: 'primary',
    route: { name: 'mobile-seasons' },
    visible: true,
  },
  {
    title: 'Leaderboard',
    icon: 'stars',
    color: 'warning',
    route: { name: 'mobile-leaderboard' },
    visible: true,
  },
  {
    title: 'Live',
    icon: 'bolt',
    color: 'accent',
    route: { name: 'mobile-live' },
    visible: true,
  },
  {
    title: 'Chat',
    icon: 'chat',
    color: 'primary',
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
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.launcher-tile {
  height: 90px;
  border-radius: 16px;
  background: #f8f9fa;
  transition: all 0.2s ease-in-out;
  border: 1px solid rgba(0, 0, 0, 0.03);

  &:active {
    transform: scale(0.95);
    background: #f0f0f0;
  }

  .q-icon {
    opacity: 0.9;
  }
}
</style>

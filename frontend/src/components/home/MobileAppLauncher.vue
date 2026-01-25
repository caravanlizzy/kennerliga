<template>
  <div class="row q-col-gutter-md q-pt-md">
    <template v-for="tile in tiles" :key="tile.title">
      <div v-if="tile.visible" class="col-6">
        <q-card
          flat
          bordered
          v-ripple
          class="launcher-tile column items-center justify-center q-pa-md cursor-pointer relative-position overflow-hidden"
          @click="navigateTo(tile.route)"
        >
          <div
            class="absolute-top-right q-ma-sm opacity-10"
            style="pointer-events: none"
          >
            <q-icon :name="tile.icon" size="64px" :color="tile.color" />
          </div>

          <q-icon
            :name="tile.icon"
            :color="tile.color"
            size="40px"
            class="q-mb-sm"
          />
          <div class="text-subtitle1 text-weight-bold text-center">
            {{ tile.title }}
          </div>
          <div class="text-caption text-grey-7 text-center">
            {{ tile.helpText }}
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
    helpText: 'Go to your current league',
    route: { name: 'my-league' },
    visible: !!userStore.user?.myCurrentLeagueId,
  },
  {
    title: 'Seasons',
    icon: 'military_tech',
    color: 'primary',
    helpText: 'View current and past standings',
    route: '/m/seasons',
    visible: true,
  },
  {
    title: 'Leaderboard',
    icon: 'stars',
    color: 'warning',
    helpText: 'See overall player rankings',
    route: '/m/leaderboard',
    visible: true,
  },
  {
    title: 'Live',
    icon: 'bolt',
    color: 'accent',
    helpText: 'Real-time active games updates',
    route: '/m/live',
    visible: true,
  },
  {
    title: 'Chat',
    icon: 'chat',
    color: 'primary',
    helpText: 'Connect with other members',
    route: '/m/chat',
    visible: true,
  },
]);

function navigateTo(route: any) {
  router.push(route);
}
</script>

<style scoped lang="scss">
.launcher-tile {
  height: 140px;
  border-radius: 16px;
  background: #ffffff;
  transition: all 0.2s ease-in-out;
  border: 1px solid rgba(0, 0, 0, 0.05);

  &:active {
    transform: scale(0.97);
    background: #f5f5f5;
  }
}

.opacity-10 {
  opacity: 0.1;
}
</style>

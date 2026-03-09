<template>
  <div class="launcher-container q-pa-md">
    <div class="staggered-list">
      <template v-for="tile in tiles" :key="tile.title">
        <div
          v-if="tile.visible"
          v-ripple
          class="launcher-tile cursor-pointer relative-position"
          :class="[
            `theme-${tile.color}`,
            tile.featured ? 'featured-tile' : ''
          ]"
          @click="navigateTo(tile.route)"
        >
          <div class="tile-inner row no-wrap items-center">
            <div class="tile-icon-box flex flex-center">
              <q-icon
                :name="tile.icon"
                size="32px"
                class="main-icon"
              />
              <div class="icon-blob"></div>
            </div>

            <div class="tile-info q-ml-lg col">
              <div class="row items-center justify-between">
                <div>
                  <div class="text-h6 text-weight-bold title-text">{{ tile.title }}</div>
                  <div class="text-caption text-grey-7 description-text">{{ tile.description }}</div>
                </div>
                <q-icon name="chevron_right" size="xs" color="grey-5" class="arrow-icon" />
              </div>
            </div>
          </div>

          <!-- Decorative element -->
          <div class="decorative-circle"></div>
        </div>
      </template>
    </div>
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
    color: 'secondary',
    route: { name: 'my-league' },
    visible: !!userStore.user?.myCurrentLeagueId,
    featured: true,
  },
  {
    title: 'Seasons',
    description: 'Browse past and current seasons',
    icon: 'military_tech',
    color: 'blue',
    route: { name: 'mobile-seasons' },
    visible: true,
    featured: false,
  },
  {
    title: 'Leaderboard',
    description: 'Check who is currently on top',
    icon: 'stars',
    color: 'orange',
    route: { name: 'mobile-leaderboard' },
    visible: true,
    featured: false,
  },
  {
    title: 'Live',
    description: 'Get info about what is going on in the leagues',
    icon: 'bolt',
    color: 'deep-purple',
    route: { name: 'mobile-live' },
    visible: true,
    featured: false,
  },
  {
    title: 'Chat',
    description: 'Connect with other league members',
    icon: 'chat',
    color: 'teal',
    route: { name: 'mobile-chat' },
    visible: true,
    featured: false,
  },
]);

function navigateTo(route: Record<string, unknown>) {
  router.push(route as any);
}
</script>

<style scoped lang="scss">
.launcher-container {
  max-width: 600px;
  margin: 0 auto;
}

.tracking-tighter {
  letter-spacing: -1.5px;
}

.staggered-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.launcher-tile {
  background: white;
  border-radius: 28px;
  padding: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(0, 0, 0, 0.04);
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
  overflow: hidden;

  &:hover {
    transform: translateX(8px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
    border-color: rgba(0, 0, 0, 0.08);

    .arrow-icon {
      transform: translateX(4px);
      color: var(--theme-color) !important;
    }

    .icon-blob {
      transform: scale(1.2) rotate(15deg);
    }
  }

  &:active {
    transform: scale(0.98) translateX(4px);
  }
}

.tile-inner {
  position: relative;
  z-index: 2;
}

.tile-icon-box {
  width: 64px;
  height: 64px;
  position: relative;

  .main-icon {
    color: var(--theme-color);
    z-index: 2;
  }

  .icon-blob {
    position: absolute;
    width: 100%;
    height: 100%;
    background: var(--theme-bg);
    border-radius: 22px;
    z-index: 1;
    transition: all 0.5s ease;
  }
}

.title-text {
  color: #1a1a1a;
  letter-spacing: -0.5px;
  margin-bottom: 2px;
}

.description-text {
  font-size: 0.8rem;
  line-height: 1.2;
}

.arrow-icon {
  transition: all 0.3s ease;
}

.decorative-circle {
  position: absolute;
  top: -20px;
  right: -20px;
  width: 80px;
  height: 80px;
  background: var(--theme-bg);
  border-radius: 50%;
  opacity: 0.3;
  z-index: 1;
}

/* Featured Tile Styles */
.featured-tile {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  padding: 24px;
  border: 2px solid var(--theme-bg);

  .tile-icon-box {
    width: 72px;
    height: 72px;
  }

  .title-text {
    font-size: 1.4rem;
  }
}

/* Theme color definitions */
.theme-secondary {
  --theme-color: #26c6da;
  --theme-bg: #e0f7fa;
}
.theme-blue {
  --theme-color: #2196f3;
  --theme-bg: #e3f2fd;
}
.theme-orange {
  --theme-color: #ff9800;
  --theme-bg: #fff3e0;
}
.theme-deep-purple {
  --theme-color: #673ab7;
  --theme-bg: #ede7f6;
}
.theme-teal {
  --theme-color: #009688;
  --theme-bg: #e0f2f1;
}

@media (min-width: 600px) {
  .staggered-list {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
  }
  .featured-tile {
    grid-column: span 2;
  }
}
</style>

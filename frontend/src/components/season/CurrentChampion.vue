<template>
  <div
    v-if="champion"
    class="champion-card-container"
    :class="{ 'is-mobile': isMobile }"
    @click="navigateToSeason"
  >
    <!-- Tooltip -->
    <q-tooltip class="bg-amber-9 text-white shadow-10" anchor="bottom middle" self="top middle" :offset="[0, 8]">
      <div class="column items-center q-pa-xs">
        <q-icon name="emoji_events" size="24px" class="q-mb-xs" />
        <div class="text-weight-bold">Current Champion: {{ champion.username }}</div>
        <div class="text-caption">Click to view {{ champion.seasonName }} results</div>
      </div>
    </q-tooltip>

    <div class="champion-card-inner row no-wrap items-center">
      <!-- Icon/Avatar Section -->
      <div class="champion-icon-wrapper flex flex-center">
        <div class="crown-overlay">
          <q-icon name="workspace_premium" size="18px" color="amber-8" />
        </div>
        <UserAvatar
          :display-username="champion.username"
          size="34px"
          shape="squircle"
          class="champion-avatar"
        />
      </div>

      <!-- Text Content Section -->
      <div class="champion-info-section column justify-center q-ml-sm" v-if="!isMobile">
        <div class="label-row row no-wrap items-center">
          <span class="champion-label">CURRENT CHAMPION</span>
          <q-icon name="star" size="10px" color="amber-8" class="q-ml-xs" />
        </div>
        <div class="name-row row no-wrap items-baseline">
          <span class="champion-name">{{ champion.username }}</span>
          <span class="season-tag" v-if="champion.seasonName">
            {{ champion.seasonName }}
          </span>
        </div>
      </div>

      <!-- Mobile Minimal Text -->
      <div class="mobile-info q-ml-xs" v-if="isMobile">
        <span class="champion-name">{{ champion.username }}</span>
      </div>

      <!-- Action Icon (Desktop) -->
      <div class="action-arrow q-ml-sm" v-if="!isMobile">
        <q-icon name="chevron_right" size="16px" color="grey-5" />
      </div>
    </div>

    <!-- Shine Effect -->
    <div class="shine-effect"></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { api } from 'boot/axios';
import { fetchSeasons } from 'src/services/seasonService';
import { useResponsive } from 'src/composables/responsive';
import UserAvatar from 'components/ui/UserAvatar.vue';

interface ChampionInfo {
  username: string;
  seasonName: string;
  seasonId: number;
}

const champion = ref<ChampionInfo | null>(null);
const { isMobile } = useResponsive();
const router = useRouter();

function navigateToSeason() {
  if (champion.value?.seasonId) {
    router.push({
      name: 'season-overview',
      params: { id: champion.value.seasonId },
    });
  }
}

async function loadCurrentChampion() {
  try {
    const seasons = await fetchSeasons({ status: 'DONE' });
    if (seasons.length === 0) return;

    const latestSeason = seasons.sort((a, b) => {
      if (a.year !== b.year) return b.year - a.year;
      return b.month - a.month;
    })[0];

    const { data } = await api.get(
      `season/seasons/${latestSeason.id}/league-winners/`
    );
    const level1Winner = data.winners?.find((w: any) => w.league.level === 1);

    const username = level1Winner?.winner?.username || level1Winner?.username;

    if (username) {
      champion.value = {
        username,
        seasonName:
          data.season?.name || `${latestSeason.year}-${latestSeason.month}`,
        seasonId: latestSeason.id,
      };
    }
  } catch (error) {
    console.error('Failed to load current champion:', error);
  }
}

onMounted(loadCurrentChampion);
</script>

<style scoped lang="scss">
.champion-card-container {
  position: relative;
  cursor: pointer;
  background: white;
  border-radius: 12px;
  padding: 4px 10px 4px 6px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  user-select: none;

  &:hover {
    box-shadow: 0 4px 15px rgba(255, 193, 7, 0.15);
    background: #fffdf5;

    .shine-effect {
      left: 150%;
      transition: left 0.8s ease-in-out;
    }

    .action-arrow {
      color: var(--q-primary) !important;
    }

    .champion-avatar {
      // No scale change
    }
  }

  &:active {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  &.is-mobile {
    padding: 2px 8px 2px 4px;
    border-radius: 20px;
    background: rgba(255, 193, 7, 0.05);
  }
}

.champion-card-inner {
  position: relative;
  z-index: 1;
}

.champion-icon-wrapper {
  position: relative;
  padding: 2px;
}

.crown-overlay {
  position: absolute;
  top: -8px;
  right: -6px;
  z-index: 2;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
  animation: crown-float 2s ease-in-out infinite;
}

@keyframes crown-float {
  0%, 100% { transform: translateY(0) rotate(10deg); }
  50% { transform: translateY(-2px) rotate(15deg); }
}

.champion-avatar {
  transition: transform 0.3s ease;
  background: white !important;
}

.champion-info-section {
  min-width: 0;
}

.champion-label {
  font-size: 0.65rem;
  font-weight: 800;
  color: #b08d00;
  letter-spacing: 0.06em;
  line-height: 1;
}

.champion-name {
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--q-dark);
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.season-tag {
  font-size: 0.75rem;
  color: #888;
  font-weight: 500;
  margin-left: 6px;
  background: rgba(0, 0, 0, 0.04);
  padding: 1px 6px;
  border-radius: 4px;
}

.action-arrow {
  transition: all 0.2s ease;
}

.shine-effect {
  position: absolute;
  top: 0;
  left: -150%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.4),
    transparent
  );
  transform: skewX(-20deg);
  z-index: 0;
}

.mobile-info {
  .champion-name {
    font-size: 0.85rem;
    color: var(--q-primary);
  }
}
</style>

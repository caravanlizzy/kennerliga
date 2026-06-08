<template>
  <div
    v-if="champion"
    class="champion-card-container"
    :class="{ 'is-mobile': isMobile }"
    @click="navigateToSeason"
  >
    <!-- Tooltip -->
    <q-tooltip
      class="elegant-tooltip shadow-10"
      anchor="bottom middle"
      self="top middle"
      :offset="[0, 8]"
    >
      <div class="column items-center q-pa-sm">
        <div class="row items-center q-gutter-x-sm q-mb-xs">
          <q-icon name="emoji_events" color="amber-8" size="20px" />
          <div class="text-subtitle2 text-weight-bold uppercase letter-spacing-1">Current Champion</div>
        </div>
        <div class="text-h6 text-amber-2 q-mb-xs">{{ champion.username }}</div>
        <q-separator color="white" dark inset class="full-width q-my-xs opacity-30" />
        <div class="text-caption text-grey-4 italic">
          Click to view {{ champion.seasonName }} results
        </div>
      </div>
    </q-tooltip>

    <div class="champion-card-inner row no-wrap items-center">
      <!-- Icon Section -->
      <div class="champion-icon-wrapper flex flex-center">
        <div class="crown-overlay">
          <q-icon name="military_tech" size="20px" color="grey-7" />
        </div>
      </div>

      <!-- Text Content Section -->
      <div class="champion-info-section column justify-center">
        <div class="name-row row no-wrap items-baseline">
          <span class="champion-name">{{ champion.username }}</span>
        </div>
      </div>

      <!-- Action Icon (Desktop) -->
      <div class="action-arrow q-ml-sm" v-if="!isMobile">
        <q-icon name="chevron_right" size="16px" color="grey-5" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { api } from 'boot/axios';
import { fetchSeasons } from 'src/services/seasonService';
import { useResponsive } from 'src/composables/responsive';

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
.elegant-tooltip {
  background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%);
  border: 1px solid rgba(255, 193, 7, 0.3);
  border-radius: 12px;
  padding: 8px 12px;
  max-width: 250px;
  text-align: center;
}

.letter-spacing-1 {
  letter-spacing: 1px;
}

.opacity-30 {
  opacity: 0.3;
}

.champion-card-container {
  position: relative;
  cursor: pointer;
  background: transparent;
  border: none;
  border-radius: 8px;
  padding: 4px 8px;
  margin: 0 4px;
  transition: background-color 0.2s ease;
  overflow: hidden;
  user-select: none;

  &:hover {
    background: rgba(0, 0, 0, 0.03);

    .action-arrow {
      color: var(--q-primary) !important;
    }

    .champion-name {
      color: var(--q-primary);
    }
  }

  &.is-mobile {
    padding: 2px 8px;
    margin: 0 2px;
    border-radius: 8px;
    background: transparent;
  }
}

.champion-card-inner {
  position: relative;
  z-index: 1;
}

.champion-icon-wrapper {
  position: relative;
  padding: 4px;
  width: 38px;
  height: 38px;
}

.champion-info-section {
  margin-left: 8px;
}

.is-mobile {
  .champion-icon-wrapper {
    width: 24px;
    height: 24px;
    padding: 0;
  }

  .champion-info-section {
    margin-left: 2px;
  }
}

.crown-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
}


.champion-info-section {
  min-width: 0;
}

.champion-name {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--q-dark);
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.action-arrow {
  transition: all 0.2s ease;
}

:global(.body--dark) .champion-card-container {
  background: transparent;
  border: none;

  &:hover {
    background: rgba(255, 255, 255, 0.04);
  }

  &.is-mobile {
    background: transparent;
  }

  .champion-name {
    color: #f5f5f5;
  }
}
</style>

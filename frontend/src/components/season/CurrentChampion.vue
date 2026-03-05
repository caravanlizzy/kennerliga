<template>
  <div
    v-if="champion"
    class="champion-display row no-wrap items-center q-gutter-x-sm cursor-pointer"
    :class="{ 'mobile-display': isMobile }"
    @click="navigateToSeason"
  >
    <q-tooltip class="bg-amber-9 text-white shadow-2">
      <div class="column items-center q-pa-xs">
        <q-icon name="emoji_events" size="24px" class="q-mb-xs" />
        <div class="text-weight-bold">Current Champion: {{ champion.username }}</div>
        <div class="text-caption">Click to view {{ champion.seasonName }} results</div>
      </div>
    </q-tooltip>

    <div class="row no-wrap items-center q-gutter-x-xs" v-if="isMobile">
      <span class="text-subtitle2 text-weight-bolder text-primary tracking-tight" style="font-size: 0.8rem; line-height: 1">
        {{ champion.username }}
      </span>
      <q-icon name="emoji_events" size="14px" color="amber-8" />
    </div>

    <template v-else>
      <div class="column items-end justify-center">
        <div
          class="text-caption text-grey-7 text-uppercase text-weight-bold leading-tight"
          style="font-size: 0.65rem"
        >
          Current Champion
        </div>
        <div
          class="text-subtitle2 text-weight-bolder text-primary tracking-tight leading-tight"
        >
          {{ champion.username }}
        </div>
      </div>
      <q-avatar
        size="32px"
        class="champion-avatar bg-amber-1 text-amber-9 shadow-1"
      >
        <q-icon name="emoji_events" size="20px" />
      </q-avatar>
      <div class="column items-start justify-center">
        <div
          class="text-caption text-grey-6 text-weight-medium"
          style="font-size: 0.7rem"
        >
          {{ champion.seasonName }}
        </div>
      </div>
    </template>
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
    // 1. Fetch the most recent 'DONE' season
    const seasons = await fetchSeasons({ status: 'DONE' });
    if (seasons.length === 0) return;

    // Sort by year and month descending to get the latest DONE season
    const latestSeason = seasons.sort((a, b) => {
      if (a.year !== b.year) return b.year - a.year;
      return b.month - a.month;
    })[0];

    // 2. Fetch winners for that season
    const { data } = await api.get(
      `season/seasons/${latestSeason.id}/league-winners/`
    );
    // 3. The overall champion is the winner of level 1
    const level1Winner = data.winners?.find((w: any) => w.league.level === 1);

    if (level1Winner && level1Winner.winner.username) {
      champion.value = {
        username: level1Winner.winner.username,
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
.champion-display {
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.05);

  &.mobile-display {
    padding: 2px 6px;
    background: white;
    border: 1px solid rgba(0, 0, 0, 0.12);
    border-radius: 6px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  }
}

.leading-tight {
  line-height: 1.1;
}

.champion-avatar {
  border: 2px solid #fff;
}

.cursor-pointer {
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    background: rgba(255, 255, 255, 0.8);
    border-color: var(--q-primary);
  }

  &:active {
    transform: translateY(0);
  }

  &.mobile-display:hover {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    background: #fafafa;
  }
}
</style>

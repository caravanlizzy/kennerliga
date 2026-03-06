<template>
  <div
    v-if="champion"
    class="champion-display row no-wrap items-center q-px-sm q-py-xs cursor-pointer"
    :class="{ 'mobile-display': isMobile }"
    @click="navigateToSeason"
  >
    <q-tooltip class="bg-amber-9 text-white shadow-10" anchor="bottom middle" self="top middle">
      <div class="column items-center q-pa-xs">
        <q-icon name="emoji_events" size="24px" class="q-mb-xs" />
        <div class="text-weight-bold">Current Champion: {{ champion.username }}</div>
        <div class="text-caption">Click to view {{ champion.seasonName }} results</div>
      </div>
    </q-tooltip>

    <div class="row no-wrap items-center q-gutter-x-sm" v-if="isMobile">
      <q-icon name="emoji_events" size="18px" color="amber-8" />
      <span class="text-weight-bold text-primary">{{ champion.username }}</span>
    </div>

    <template v-else>
      <q-avatar
        size="30px"
        class="champion-avatar bg-amber-1 text-amber-9"
      >
        <q-icon name="emoji_events" size="20px" />
      </q-avatar>
      <div class="column items-start justify-center q-ml-sm">
        <div
          class="text-caption text-grey-7 text-uppercase text-weight-bold leading-none q-mb-xs"
          style="font-size: 0.6rem; letter-spacing: 0.05em"
        >
          Current Champion
        </div>
        <div class="row no-wrap items-baseline">
          <span class="text-subtitle2 text-weight-bolder text-primary q-mr-xs leading-none">
            {{ champion.username }}
          </span>
          <span class="text-caption text-grey-6 text-weight-medium leading-none" style="font-size: 0.7rem">
            ({{ champion.seasonName }})
          </span>
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
  background: white;
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    border-color: rgba(255, 193, 7, 0.4);
    background: #fafafa;
  }

  &:active {
    background: #f0f0f0;
  }

  &.mobile-display {
    border-radius: 12px;
    padding: 4px 10px;
  }
}

.leading-none {
  line-height: 1;
}

.champion-avatar {
  border: 1px solid rgba(255, 193, 7, 0.2);
}
</style>

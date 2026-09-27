<template>
  <div class="season-winners">
    <!-- Loading state -->
    <div v-if="loading" class="flex flex-center q-pa-md">
      <q-spinner color="amber-8" size="28px" />
    </div>

    <!-- Empty state -->
    <div
      v-else-if="winners.length === 0"
      class="season-winners__empty q-pa-md text-caption text-grey-6"
    >
      <q-icon name="emoji_events" size="20px" class="q-mr-xs opacity-50" />
      No winners recorded yet for this season.
    </div>

    <!-- Winners content -->
    <div v-else class="winners-container" :class="{ 'has-other-leagues': otherLeagueWinners.length > 0 }">
      <!-- Season Champion (League 1 Winner) Hero Card -->
      <div
        v-if="championWinner"
        class="champion-hero"
        :class="{ 'champion-hero--me': isMe(championWinner.username) }"
      >
        <div class="champion-hero__glow"></div>
        <div class="champion-hero__content">
          <!-- Top Tag -->
          <div class="champion-hero__top row items-center justify-between no-wrap">
            <div class="champion-tag row items-center no-wrap">
              <q-icon name="emoji_events" size="15px" class="q-mr-xs text-amber-9" />
              <span class="text-weight-bolder letter-spacing-1">SEASON CHAMPION</span>
            </div>
            <LeagueLevel badge :level="championWinner.level" />
          </div>

          <!-- Champion Profile Section -->
          <div class="champion-hero__body row items-center q-gutter-x-md no-wrap">
            <div class="champion-avatar-wrap">
              <UserAvatar
                :display-username="championWinner.profileName || championWinner.username"
                :navigation-name="championWinner.username"
                size="52px"
                border
              />
              <div class="champion-crown-pill" title="Season Champion">
                <q-icon name="workspace_premium" size="14px" color="amber-9" />
              </div>
            </div>

            <div class="champion-hero__info column justify-center ellipsis">
              <div
                class="champion-name ellipsis text-weight-bolder"
                :class="{ 'text-primary': isMe(championWinner.username) }"
                :title="championWinner.profileName || championWinner.username"
              >
                {{ championWinner.profileName || championWinner.username }}
              </div>
              <div
                v-if="championWinner.profileName && championWinner.username && championWinner.profileName !== championWinner.username"
                class="champion-handle ellipsis text-caption text-grey-7"
              >
                @{{ championWinner.username }}
              </div>
              <div
                v-if="championWinner.points != null"
                class="champion-score text-caption text-weight-bold text-amber-10 q-mt-xs"
              >
                {{ championWinner.points }} {{ Number(championWinner.points) === 1 ? 'pt' : 'pts' }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Other League Champions (L2, L3, L4, ...) -->
      <div v-if="otherLeagueWinners.length > 0" class="other-leagues-panel">
        <div class="other-leagues-panel__header row items-center q-gutter-x-xs q-mb-sm">
          <q-icon name="military_tech" size="15px" color="grey-7" />
          <span class="text-caption text-weight-bold text-grey-8 uppercase letter-spacing-1">
            League Champions
          </span>
        </div>

        <div class="other-leagues-grid">
          <div
            v-for="item in otherLeagueWinners"
            :key="`${item.username}-${item.level}`"
            class="league-card row items-center justify-between"
            :class="{ 'league-card--me': isMe(item.username) }"
          >
            <div class="row items-center q-gutter-x-sm no-wrap ellipsis">
              <LeagueLevel badge :level="item.level" />
              <UserAvatar
                :display-username="item.profileName || item.username"
                :navigation-name="item.username"
                size="28px"
                border
              />
              <div class="column no-wrap ellipsis">
                <span
                  class="league-card__name text-body2 text-weight-bold ellipsis"
                  :class="{ 'text-primary': isMe(item.username) }"
                >
                  {{ item.profileName || item.username }}
                </span>
                <span
                  v-if="item.profileName && item.username && item.profileName !== item.username"
                  class="league-card__handle text-caption text-grey-6 ellipsis"
                >
                  @{{ item.username }}
                </span>
              </div>
            </div>
            <div
              v-if="item.points != null"
              class="league-card__points text-caption text-weight-bold text-grey-8 q-ml-sm shrink-0"
            >
              {{ item.points }} pts
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { fetchSeasonLeagueWinners } from 'src/services/seasonService';
import LeagueLevel from 'components/season/LeagueLevel.vue';
import UserAvatar from 'components/ui/UserAvatar.vue';
import { useUserStore } from 'stores/userStore';

interface WinnerEntry {
  profileId: number;
  username: string;
  profileName: string;
  level: number;
  leagueId: number;
  points: string | number | null;
}

const props = defineProps<{
  seasonId: number;
}>();

const loading = ref<boolean>(false);
const winners = ref<WinnerEntry[]>([]);
const userStore = useUserStore();

function isMe(username: string): boolean {
  return Boolean(username && userStore.isMe(username));
}

async function loadWinners() {
  if (!props.seasonId) {
    winners.value = [];
    return;
  }
  loading.value = true;
  try {
    const data = await fetchSeasonLeagueWinners(props.seasonId);
    winners.value = (data.winners ?? [])
      .slice()
      .sort((a, b) => a.league.level - b.league.level)
      .map((x) => ({
        profileId: x.winner?.profile_id ?? 0,
        username: x.winner?.username || '',
        profileName: x.winner?.profile_name || '',
        level: x.league.level,
        leagueId: x.league.id,
        points: x.league_points ?? null,
      }))
      .filter((x) => x.username !== '');
  } catch (err) {
    console.error('Failed to load season winners:', err);
    winners.value = [];
  } finally {
    loading.value = false;
  }
}

onMounted(loadWinners);
watch(() => props.seasonId, loadWinners);

const championWinner = computed(() => {
  return winners.value.find((w) => w.level === 1) || winners.value[0] || null;
});

const otherLeagueWinners = computed(() => {
  if (!championWinner.value) return [];
  return winners.value.filter((w) => w.level !== championWinner.value?.level);
});
</script>

<style scoped lang="scss">
.season-winners {
  width: 100%;
}

.season-winners__empty {
  border: 1px dashed rgba(0, 0, 0, 0.12);
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.02);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60px;
}

/* Layout Container */
.winners-container {
  display: flex;
  flex-direction: column;
  gap: 12px;

  &.has-other-leagues {
    @media (min-width: 768px) {
      display: grid;
      grid-template-columns: minmax(280px, 1.2fr) minmax(260px, 1.8fr);
      gap: 16px;
      align-items: stretch;
    }
  }
}

/* Champion Hero Card */
.champion-hero {
  position: relative;
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 45%, #ffffff 100%);
  border: 1px solid rgba(245, 158, 11, 0.45);
  border-radius: 12px;
  padding: 12px 14px;
  box-shadow: 0 3px 12px rgba(245, 158, 11, 0.12), 0 1px 3px rgba(0, 0, 0, 0.04);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  @media (max-width: 599px) {
    padding: 10px 12px;
  }

  &--me {
    border-color: var(--q-primary);
    box-shadow: 0 0 0 1px var(--q-primary), 0 4px 14px rgba(245, 158, 11, 0.18);
  }

  &__glow {
    position: absolute;
    top: -20px;
    right: -20px;
    width: 100px;
    height: 100px;
    background: radial-gradient(circle, rgba(251, 191, 36, 0.25) 0%, rgba(251, 191, 36, 0) 70%);
    pointer-events: none;
  }

  &__content {
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
}

.champion-tag {
  background: #fef3c7;
  border: 1px solid #fde68a;
  color: #92400e;
  font-size: 0.68rem;
  padding: 2px 8px;
  border-radius: 20px;
  line-height: 1.2;
}

.champion-avatar-wrap {
  position: relative;
  display: inline-flex;
  flex-shrink: 0;
}

.champion-crown-pill {
  position: absolute;
  bottom: -3px;
  right: -3px;
  background: #fffbeb;
  border: 1.5px solid #fde68a;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
}

.champion-name {
  font-size: 1.05rem;
  line-height: 1.2;
  color: #1e293b;
}

.champion-handle {
  font-size: 0.72rem;
  line-height: 1.1;
  margin-top: 1px;
}

.champion-score {
  font-size: 0.75rem;
  background: rgba(245, 158, 11, 0.15);
  display: inline-block;
  align-self: flex-start;
  padding: 1px 6px;
  border-radius: 4px;
}

/* Other Leagues Panel */
.other-leagues-panel {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.other-leagues-panel__header {
  letter-spacing: 0.5px;
  font-size: 0.7rem;
}

.other-leagues-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 8px;

  @media (max-width: 599px) {
    grid-template-columns: 1fr;
    gap: 6px;
  }
}

.league-card {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  padding: 6px 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
  transition: background-color 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;

  &:hover {
    background: #f8fafc;
    border-color: rgba(0, 0, 0, 0.14);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
  }

  &--me {
    border-color: var(--q-primary);
    background: rgba(var(--q-primary), 0.04);
  }

  &__name {
    font-size: 0.8rem;
    line-height: 1.2;
  }

  &__handle {
    font-size: 0.65rem;
    line-height: 1;
  }

  &__points {
    font-size: 0.72rem;
  }
}

.letter-spacing-1 {
  letter-spacing: 0.5px;
}
</style>

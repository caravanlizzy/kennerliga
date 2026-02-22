<template>
  <section class="season-winners">
    <header class="season-winners__header">
      <h2
        class="season-winners__title q-ma-none text-h5 text-dark text-weight-bold"
      >
        Season {{ season }}
      </h2>
    </header>

    <div
      v-if="winners.length === 0"
      class="season-winners__empty q-pa-sm text-grey-8"
    >
      No winners recorded yet.
    </div>

    <template v-else>
      <!-- Season Winner (Level 1 Winner) -->
      <div v-if="seasonWinner" class="season-winner-crown text-center q-mb-lg">
        <div class="relative-position display-inline-block">
          <q-icon name="workspace_premium" color="amber-8" size="64px" class="crown-icon" />
          <q-badge color="amber-1" text-color="amber-9" floating class="text-weight-bold" style="top: 10px; right: -5px">
            Winner
          </q-badge>
        </div>
        <div class="text-h4 text-weight-bolder text-dark q-mt-sm">{{ seasonWinner.username }}</div>
        <div class="text-subtitle1 text-grey-7 text-uppercase letter-spacing-1">Season Winner</div>
      </div>

      <q-separator class="q-my-md" />
      <div class="text-overline text-grey-6 text-center">League Winners</div>

      <!-- Podium (top 3) -->
      <div class="podium q-gutter-sm" aria-label="Podium">
        <div
          v-for="spot in podiumSpots"
          :key="spot.level"
          class="podium__spot"
          :class="`podium__spot--${spot.class}`"
          :aria-label="`${spot.label} place`"
        >
          <div class="podium__name text-weight-bold text-capitalize">
            {{ spot.winner?.username || '-' }}
          </div>
          <div v-if="spot.winner?.profile_name && spot.winner.profile_name !== spot.winner.username" class="text-caption text-grey-6" style="font-size: 0.7rem">
            {{ spot.winner.profile_name }}
          </div>
          <div class="podium__base q-pa-sm text-weight-bold">L{{ spot.level }}</div>
        </div>
      </div>

      <!-- Next in line -->
      <div v-if="restOfLeagues.length" class="next q-mt-sm">
        <ol class="next__list q-pa-none q-ma-none q-mt-xs">
          <li
            v-for="item in restOfLeagues"
            :key="`${item.username}-${item.level}`"
            class="next__item q-pa-sm q-gutter-sm"
          >
            <span class="next__badge bg-grey-3 text-weight-bolder">
              L{{ item.level }}
            </span>
            <div class="column">
              <span class="next__name text-capitalize text-weight-bold">{{ item.username }}</span>
              <span v-if="item.profile_name && item.profile_name !== item.username" class="text-caption text-grey-6" style="font-size: 0.7rem">
                {{ item.profile_name }}
              </span>
            </div>
          </li>
        </ol>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { api } from 'boot/axios';

type LeagueWinnerApiResponse = {
  season: { id: number; name: string; status: string };
  winners: Array<{
    league: { id: number; level: number };
    winner: string | null;
    username: string | null;
    profile_name: string | null;
    league_points: number | null;
  }>;
};

const props = defineProps<{
  seasonId: number;
}>();

const season = ref<string>('');
const winners = ref<Array<{ username: string; profile_name: string; level: number }>>([]);

onMounted(async () => {
  if (!props.seasonId) return;
  const { data } = await api.get<LeagueWinnerApiResponse>(
    `season/seasons/${props.seasonId}/league-winners/`
  );

  season.value = data.season?.name ?? '';

  // winners list (only non-null winners), ordered by league.level
  winners.value = (data.winners ?? [])
    .slice()
    .sort((a, b) => a.league.level - b.league.level)
    .map((x) => ({
      username: x.winner?.username || x.username || '',
      profile_name: x.winner?.profile_name || x.profile_name || '',
      level: x.league.level
    }))
    .filter((x) => x.username !== '');
});

const seasonWinner = computed(() => winners.value.find(w => w.level === 1));

const podiumSpots = computed(() => {
  const levels = [2, 1, 3];
  const classes = ['second', 'first', 'third'];
  const labels = ['Second', 'First', 'Third'];

  return levels.map((lvl, idx) => ({
    level: lvl,
    class: classes[idx],
    label: labels[idx],
    winner: winners.value.find(w => w.level === lvl)
  }));
});

const restOfLeagues = computed(() => {
  return winners.value.filter(w => ![1, 2, 3].includes(w.level));
});
</script>

<style scoped>
.season-winner-crown {
  animation: fadeInDown 0.8s ease-out;
}

.crown-icon {
  animation: float 3s ease-in-out infinite;
}

.display-inline-block {
  display: inline-block;
}

.letter-spacing-1 {
  letter-spacing: 1px;
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0px); }
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translate3d(0, -20px, 0);
  }
  to {
    opacity: 1;
    transform: translate3d(0, 0, 0);
  }
}

.season-winners {
  display: grid;
  gap: 16px;
}

.season-winners__header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.season-winners__title {
  font-size: 20px;
}

.season-winners__empty {
  border: 1px dashed rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  opacity: 0.9;
}

/* Podium */
.podium {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  align-items: end;
}

.podium__spot {
  display: grid;
  gap: 8px;
  justify-items: center;
  text-align: center;
}

.podium__rank {
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  border-radius: 999px;
}

.podium__base {
  width: 100%;
  border-radius: 12px;
  font-weight: 800;
  letter-spacing: 0.3px;
}

/* Heights/colors to suggest podium */
.podium__spot--first .podium__base {
  min-height: 120px;
  background: #f6d365; /* gold-ish */
}

.podium__spot--second .podium__base {
  min-height: 95px;
  background: #d7dde8; /* silver-ish */
}

.podium__spot--third .podium__base {
  min-height: 80px;
  background: #d6a77a; /* bronze-ish */
}

/* Next in line */
.next {
  display: grid;
  gap: 8px;
}

.next__list {
  list-style: none;
  display: grid;
  gap: 6px;
}

.next__item {
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.04);
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid transparent;
}

.next__badge {
  flex: 0 0 auto;
  min-width: 42px;
  height: 26px;
  display: inline-grid;
  place-items: center;
  border-radius: 999px;
  letter-spacing: 0.3px;
  font-size: 12px;
}

/* Give positions 4 and 5 a bit more highlight */
.next__item--pos4 {
  background: rgba(246, 211, 101, 0.18);
  border-color: rgba(246, 211, 101, 0.45);
}

.next__item--pos4 .next__badge {
  background: rgba(246, 211, 101, 0.6);
}

.next__item--pos5 {
  background: rgba(215, 221, 232, 0.22);
  border-color: rgba(215, 221, 232, 0.8);
}

.next__item--pos5 .next__badge {
  background: rgba(215, 221, 232, 0.95);
}
</style>

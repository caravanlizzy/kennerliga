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
      <!-- Podium (top 3) -->
      <div class="podium q-gutter-sm" aria-label="Podium">
        <div
          v-if="top3[1]"
          class="podium__spot podium__spot--second"
          aria-label="Second place"
        >
          <div class="podium__name text-weight-bold text-capitalize">
            {{ top3[1].profile_name }}
          </div>
          <div class="podium__base q-pa-sm text-weight-bold">L2</div>
        </div>

        <div
          v-if="top3[0]"
          class="podium__spot podium__spot--first"
          aria-label="First place"
        >
          <div class="podium__name text-weight-bold text-capitalize">
            {{ top3[0].profile_name }}
          </div>
          <div class="podium__base q-pa-sm text-weight-bold">L1</div>
        </div>

        <div
          v-if="top3[2]"
          class="podium__spot podium__spot--third"
          aria-label="Third place"
        >
          <div class="podium__name text-weight-bold text-capitalize">
            {{ top3[2].profile_name }}
          </div>
          <div class="podium__base q-pa-sm text-weight-bold">L3</div>
        </div>
      </div>

      <!-- Next in line -->
      <div v-if="rest.length" class="next q-mt-sm">
        <ol class="next__list q-pa-none q-ma-none q-mt-xs">
          <li
            v-for="(name, idx) in rest"
            :key="`${name}-${idx}`"
            class="next__item q-pa-sm q-gutter-sm"
            :class="{
              'next__item--pos4': idx === 0,
              'next__item--pos5': idx === 1,
            }"
          >
            <span class="next__badge bg-grey-3 text-weight-bolder">
              {{ levelLabel(idx + 4) }}
            </span>
            <span class="next__name text-capitalize">{{ name }}</span>
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
    league_points: number | null;
  }>;
};

const props = defineProps<{
  seasonId: number;
}>();

const season = ref<string>('');
const winners = ref<string[]>([]);

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
    .map((x) => x.winner)
    .filter((x): x is string => Boolean(x));
});

const top3 = computed(() => winners.value.slice(0, 3));
const rest = computed(() => winners.value.slice(3));
const levelLabel = (pos: number) => `L${pos}`;
</script>

<style scoped>
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

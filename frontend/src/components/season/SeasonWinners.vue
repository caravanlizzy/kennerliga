<template>
  <section class="season-winners">
    <header class="season-winners__header">
      <h2 class="season-winners__title">Season Winners</h2>
      <div class="season-winners__season">{{ season }}</div>
    </header>
    {{data}}

    <div v-if="winners.length === 0" class="season-winners__empty">
      No winners recorded yet.
    </div>

    <template v-else>
      <!-- Podium (top 3) -->
      <div class="podium" aria-label="Podium">
        <div
          v-if="top3[1]"
          class="podium__spot podium__spot--second"
          aria-label="Second place"
        >
          <div class="podium__rank">2</div>
          <div class="podium__name">{{ top3[1] }}</div>
          <div class="podium__base">2nd</div>
        </div>

        <div
          v-if="top3[0]"
          class="podium__spot podium__spot--first"
          aria-label="First place"
        >
          <div class="podium__rank">1</div>
          <div class="podium__name">{{ top3[0] }}</div>
          <div class="podium__base">1st</div>
        </div>

        <div
          v-if="top3[2]"
          class="podium__spot podium__spot--third"
          aria-label="Third place"
        >
          <div class="podium__rank">3</div>
          <div class="podium__name">{{ top3[2] }}</div>
          <div class="podium__base">3rd</div>
        </div>
      </div>

      <!-- Next in line -->
      <div v-if="rest.length" class="next">
        <h3 class="next__title">Next in line</h3>
        <ol class="next__list" :start="4">
          <li v-for="(name, idx) in rest" :key="`${name}-${idx}`" class="next__item">
            <span class="next__name">{{ name }}</span>
          </li>
        </ol>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';

const winners = ref<string[]>(['marc', 'john', 'peter']);
const season = ref('2025_S1');

const top3 = computed(() => winners.value.slice(0, 3));
const rest = computed(() => winners.value.slice(3));
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
  margin: 0;
  font-size: 20px;
  font-weight: 700;
}

.season-winners__season {
  font-size: 12px;
  opacity: 0.75;
}

.season-winners__empty {
  padding: 12px;
  border: 1px dashed rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  opacity: 0.8;
}

/* Podium */
.podium {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  align-items: end;
  gap: 12px;
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
  font-weight: 800;
  background: rgba(0, 0, 0, 0.06);
}

.podium__name {
  font-weight: 700;
  text-transform: capitalize;
}

.podium__base {
  width: 100%;
  border-radius: 12px;
  padding: 12px 10px;
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

.next__title {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
  opacity: 0.9;
}

.next__list {
  margin: 0;
  padding-left: 20px;
  display: grid;
  gap: 6px;
}

.next__item {
  padding: 8px 10px;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.04);
}

.next__name {
  text-transform: capitalize;
}
</style>

<script setup lang="ts">
import { ref } from 'vue';

async function fetchWinners() {
  const { data } = api('season/seasons/1/league-winners')
}
const winners = ref( [ 'marc', 'john', 'peter'])
const season = ref("2025_S1")
</script>

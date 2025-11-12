<template>
  <div>
    <div class="row items-center q-mb-md">
      <q-btn flat round icon="arrow_back" @click="router.back()" class="q-mr-sm" />
      <div class="text-h5 text-weight-bold">Manage Season {{ season?.name || '…' }}</div>
      <q-space />
      <q-badge v-if="leagues?.length" class="q-ml-md" align="middle">{{ leagues.length }} leagues</q-badge>
    </div>

    <q-skeleton v-if="loading" type="rect" class="q-mb-md" height="56px" />
    <q-skeleton v-if="loading" type="rect" class="q-mb-md" height="160px" />

    <div v-else>
      <div v-if="leagues.length === 0" class="text-grey-7 q-mt-lg">
        No leagues found for this season.
      </div>

      <div class="row q-col-gutter-md">
        <div
          v-for="league in leagues"
          :key="league.id"
          class="col-12 col-sm-6 col-md-4"
        >
          <LeagueList :league="league"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { fetchLeaguesBySeason, fetchSeason } from 'src/services/seasonService';
import LeagueList from 'components/season/LeagueList.vue';

interface Member { id: number|string; username?: string; name?: string }
interface League { id: number|string; level: number|string; members?: Member[] }
interface Season { id?: number|string; name?: string }

const route = useRoute();
const router = useRouter();
const seasonId = Number(route.params.id);

const leagues = ref<League[]>([]);
const season = ref<Season>({});
const loading = ref(true);
const error = ref<string | null>(null);



onMounted(async () => {
  try {
    loading.value = true;
    season.value = await fetchSeason(seasonId);
    leagues.value = await fetchLeaguesBySeason(seasonId);
  } catch (e: any) {
    error.value = e?.message || 'Failed to load season or leagues.';
  } finally {
    loading.value = false;
  }
});
</script>

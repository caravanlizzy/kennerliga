
<template>
  <div>
    <!-- Header -->
    <div class="row items-center q-mb-lg">
      <q-btn
        flat
        round
        icon="arrow_back"
        @click="router.back()"
        class="q-mr-md"
      />
      <div class="text-h5 text-weight-bold">
        Manage Season {{ season?.name || '...' }}
      </div>
      <q-space />
      <q-badge
        v-if="season?.status"
        color="teal"
        :label="season.status"
        class="q-mr-sm"
      />
      <q-badge
        v-if="leagues?.length"
        color="primary"
        :label="`${leagues.length} ${leagues.length === 1 ? 'league' : 'leagues'}`"
      />
    </div>

    <!-- Error State -->
    <q-banner
      v-if="error && !loading"
      rounded
      class="bg-negative text-white q-mb-md"
    >
      <template v-slot:avatar>
        <q-icon name="error" />
      </template>
      {{ error }}
    </q-banner>

    <!-- Loading State -->
    <div v-if="loading" class="row q-col-gutter-md">
      <div
        v-for="i in 3"
        :key="i"
        class="col-12 col-sm-6 col-md-4"
      >
        <q-skeleton type="rect" height="280px" />
      </div>
    </div>

    <!-- Content -->
    <div v-else-if="!error">
      <!-- Empty State -->
      <div v-if="leagues.length === 0" class="text-center q-mt-xl q-mb-xl q-pa-xl">
        <q-icon name="sports" size="80px" color="grey-5" class="q-mb-md" />
        <div class="text-h6 text-weight-medium text-grey-7 q-mb-sm">
          No leagues found for this season
        </div>
        <div class="text-body2 text-grey-6">
          Create a league to get started
        </div>
      </div>

      <!-- Leagues Grid -->
      <div v-else class="row q-col-gutter-md">
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

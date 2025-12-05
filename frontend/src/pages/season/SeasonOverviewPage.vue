<template>
  <div class="q-pa-md bg-white">
    <!-- Header -->
    <div class="row items-center q-mb-md">
      <q-btn
        flat
        dense
        round
        icon="arrow_back"
        color="grey-7"
        @click="router.back()"
        class="q-mr-sm"
      />
      <div class="text-subtitle1 text-weight-medium text-grey-8">
        Manage Season {{ season?.name || '...' }}
      </div>
      <q-space />
      <q-badge
        v-if="season?.status"
        outline
        color="teal-6"
        :label="season.status"
        class="q-mr-xs text-caption"
      />
      <q-badge
        v-if="leagues?.length"
        outline
        color="grey-6"
        :label="`${leagues.length} ${leagues.length === 1 ? 'league' : 'leagues'}`"
        class="text-caption"
      />
    </div>

    <q-separator class="q-mb-md" />

    <!-- Error State -->
    <q-banner
      v-if="error && !loading"
      dense
      rounded
      class="bg-red-1 text-red-8 q-mb-sm"
    >
      <template v-slot:avatar>
        <q-icon name="error_outline" color="red-5" size="xs" />
      </template>
      <span class="text-caption">{{ error }}</span>
    </q-banner>

    <!-- Loading State -->
    <div v-if="loading" class="row q-col-gutter-sm">
      <div
        v-for="i in 3"
        :key="i"
        class="col-12 col-sm-6 col-md-4"
      >
        <q-skeleton type="rect" height="180px" class="rounded-borders" />
      </div>
    </div>

    <!-- Content -->
    <div v-else-if="!error">
      <!-- Empty State -->
      <div v-if="leagues.length === 0" class="text-center q-py-xl">
        <q-icon name="sports" size="48px" color="grey-4" class="q-mb-sm" />
        <div class="text-body2 text-grey-6 q-mb-xs">
          No leagues found for this season
        </div>
        <div class="text-caption text-grey-5">
          Create a league to get started
        </div>
      </div>

      <!-- Leagues Grid -->
      <div v-else class="row q-col-gutter-sm">
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
interface Season { id?: number|string; name?: string; status?: string }

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

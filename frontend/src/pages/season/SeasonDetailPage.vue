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
          <q-card bordered flat class="league-card cursor-pointer" @click="goToLeague(league)">
            <q-card-section class="row items-center q-gutter-sm">
              <q-avatar color="primary" text-color="white" size="40px">
                L{{ league.level }}
              </q-avatar>
              <div class="col">
                <div class="text-subtitle1 text-weight-medium">League {{ league.level }}</div>
                <div class="text-caption text-grey-7">ID: {{ league.id }}</div>
              </div>
              <q-chip square outline icon="group" class="q-ml-auto">{{ league.members?.length || 0 }}</q-chip>
            </q-card-section>

            <q-separator />

            <q-card-section>
              <div class="text-caption text-grey-7 q-mb-xs">Members</div>
              <div class="row q-col-gutter-xs">
                <q-chip
                  v-for="m in (league.members || [])"
                  :key="m.id"
                  dense
                  clickable
                  @click.stop
                  icon="person"
                  class="q-mr-xs q-mb-xs"
                >
                  {{ m.username || m.name }}
                </q-chip>
              </div>
            </q-card-section>

            <q-separator />

            <q-card-actions align="right">
              <q-btn flat icon="open_in_new" label="Open" @click.stop="goToLeague(league)" />
            </q-card-actions>
          </q-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { fetchLeaguesBySeason, fetchSeason } from 'src/services/seasonService';

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

function goToLeague(league: League) {
  // Adjust the route target to your app's routes
  // Option A: named route
  try {
    router.push({ name: 'ManageLeague', params: { id: league.id } });
  } catch (e) {
    // Option B: fallback path-based navigation
    router.push(`/leagues/${league.id}`);
  }
}

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

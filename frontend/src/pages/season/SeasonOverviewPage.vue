<template>
  <div class="q-pa-md">
    <!-- Header -->
    <div class="row items-center q-mb-md">
      <KennerButton
        flat
        dense
        round
        icon="arrow_back"
        color="grey-7"
        @click="router.back()"
        class="q-mr-sm"
      />
      <div class="text-h5 text-weight-bold">
        Manage Season {{ season?.name || '…' }}
      </div>
      <q-space />
      <div v-if="leagues?.length" class="row items-center q-gutter-x-sm">
        <q-badge align="middle">{{ leagues.length }} leagues</q-badge>
        <q-badge
          v-if="season?.status"
          outline
          :color="statusColor"
          :label="season.status"
        />
      </div>
    </div>

    <!-- Error State -->
    <q-banner
      v-if="error && !loading"
      dense
      rounded
      class="bg-red-1 text-red-8 q-mb-md"
    >
      <template v-slot:avatar>
        <q-icon name="error_outline" color="red-5" size="xs" />
      </template>
      <span class="text-caption">{{ error }}</span>
    </q-banner>

    <!-- Loading State -->
    <div v-if="loading">
      <q-skeleton type="rect" class="q-mb-md" height="56px" />
      <q-skeleton type="rect" class="q-mb-md" height="160px" />
    </div>

    <!-- Content -->
    <div v-else-if="!error">
      <!-- Registered Members Section -->
      <div v-if="participants.length > 0" class="q-mb-lg">
        <div class="text-caption text-grey-7 q-mb-xs uppercase text-weight-bold">Registered Members ({{ participants.length }})</div>
        <div class="row q-col-gutter-xs">
          <q-chip
            v-for="p in participants"
            :key="p.id"
            dense
            icon="person"
            class="q-mr-xs q-mb-xs"
          >
            {{ p.profile_name }}
          </q-chip>
        </div>
      </div>

      <q-separator v-if="participants.length > 0" class="q-mb-lg" />

      <!-- Leagues Grid -->
      <div v-if="leagues.length === 0" class="text-grey-7 q-mt-lg">
        No leagues found for this season.
      </div>
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
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { fetchLeaguesBySeason, fetchSeason, fetchSeasonParticipants } from 'src/services/seasonService';
import LeagueList from 'components/season/LeagueList.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { TSeasonDto, TLeagueDto, TSeasonParticipantDto } from 'src/types';

const route = useRoute();
const router = useRouter();
const seasonId = Number(route.params.id);

const leagues = ref<TLeagueDto[]>([]);
const season = ref<TSeasonDto | null>(null);
const participants = ref<TSeasonParticipantDto[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

const statusColor = computed(() => {
  switch (season.value?.status) {
    case 'OPEN': return 'teal-6';
    case 'RUNNING': return 'primary';
    case 'DONE': return 'grey-7';
    default: return 'grey-6';
  }
});

onMounted(async () => {
  try {
    loading.value = true;
    const [seasonData, leagueData, participantData] = await Promise.all([
      fetchSeason(seasonId),
      fetchLeaguesBySeason(seasonId),
      fetchSeasonParticipants(seasonId)
    ]);
    season.value = seasonData || null;
    leagues.value = leagueData;
    participants.value = participantData;
  } catch (e: any) {
    error.value = e?.message || 'Failed to load season details.';
  } finally {
    loading.value = false;
  }
});
</script>

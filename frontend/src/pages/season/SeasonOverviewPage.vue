<template>
  <q-page class="q-pa-md">
    <!-- Header Area -->
    <div class="row items-center justify-between q-mb-lg">
      <div class="row items-center q-gutter-x-md">
        <div class="column">
          <div class="row items-center q-gutter-x-xs">
            <q-icon name="military_tech" size="sm" color="primary" />
            <span class="text-overline text-grey-7">Season Overview</span>
          </div>
          <div class="text-h4 text-weight-bolder text-dark tracking-tighter">
            {{ season?.name || '…' }}
          </div>
        </div>
      </div>
      <div class="row items-center q-gutter-x-sm">
        <div
          v-if="seasonStatusLabel"
          class="q-px-md q-py-xs rounded-borders-12 text-weight-bold text-caption shadow-1"
          :class="`bg-${statusColor} text-white`"
        >
          {{ seasonStatusLabel }}
        </div>
        <KennerButton
          v-if="!loading && season"
          flat
          icon="refresh"
          shape="squircle"
          color="primary"
          size="md"
          @click="load"
        >
          <KennerTooltip>Refresh</KennerTooltip>
        </KennerButton>
      </div>
    </div>

    <!-- Error State -->
    <ErrorDisplay v-if="error && !loading" :error="error" class="q-mb-md" />

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center q-my-xl">
      <LoadingSpinner />
    </div>

    <!-- Content -->
    <div v-else-if="!error && season">
      <!-- League Distribution - inline stat pills -->
      <div class="row items-center q-gutter-x-md q-gutter-y-sm q-mb-md">
        <div class="row items-center q-gutter-x-xs">
          <q-icon name="hub" color="primary" size="sm" />
          <span class="text-overline text-grey-7 text-weight-bold">League Distribution</span>
        </div>
        <div class="row items-center q-gutter-x-sm q-px-md q-py-xs bg-grey-1 rounded-borders-12 border-subtle">
          <q-icon name="groups" color="grey-7" size="xs" />
          <span class="text-caption text-grey-8">Total Leagues</span>
          <span class="text-subtitle2 text-weight-bold">{{ leagues.length }}</span>
        </div>
        <div class="row items-center q-gutter-x-sm q-px-md q-py-xs bg-grey-1 rounded-borders-12 border-subtle">
          <q-icon name="person" color="grey-7" size="xs" />
          <span class="text-caption text-grey-8">Participants</span>
          <span class="text-subtitle2 text-weight-bold">{{ participants.length }}</span>
        </div>
      </div>

      <!-- Champions Section -->
      <div class="q-mb-lg">
        <ContentSection
          title="Champions"
          icon="emoji_events"
          color="amber-8"
          style="margin-top: 0"
        >
          <SeasonWinners :season-id="seasonId" />
        </ContentSection>
      </div>

      <!-- Leagues: standings + match results integrated per league -->
      <div class="q-mt-xl">
        <div class="row items-center q-gutter-x-xs q-px-md q-mb-sm">
          <q-icon name="leaderboard" color="primary" size="sm" />
          <span class="text-overline text-grey-7 text-weight-bold">League Standings &amp; Results</span>
        </div>
        <SeasonStandings :season-id="seasonId" mode="results" />
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { fetchLeaguesBySeason, fetchSeason, fetchSeasonParticipants } from 'src/services/seasonService';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import ContentSection from 'components/base/ContentSection.vue';
import ErrorDisplay from 'components/base/ErrorDisplay.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import SeasonStandings from 'components/season/SeasonStandings.vue';
import SeasonWinners from 'components/season/SeasonWinners.vue';
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
  if (isSeasonCompleted.value) return 'grey-7';
  switch (season.value?.status) {
    case 'OPEN': return 'teal-6';
    case 'RUNNING': return 'primary';
    case 'DONE': return 'grey-7';
    default: return 'grey-6';
  }
});

const isSeasonCompleted = computed(() => season.value?.is_completed ?? false);

const seasonStatusLabel = computed(() => {
  if (isSeasonCompleted.value) return 'COMPLETE';
  return season.value?.status || '';
});

async function load() {
  try {
    loading.value = true;
    error.value = null;
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
}

onMounted(load);
</script>

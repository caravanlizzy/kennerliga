<template>
  <q-page class="q-pa-md">
    <!-- Header Area -->
    <div class="row items-center justify-between q-mb-md">
      <div class="row items-center q-gutter-x-sm">
        <KennerButton
          flat
          icon="arrow_back"
          round
          color="grey-7"
          size="md"
          @click="router.back()"
        >
          <KennerTooltip>Back</KennerTooltip>
        </KennerButton>
        <q-icon name="military_tech" size="md" color="primary" />
        <div class="text-h4 text-weight-bolder text-dark tracking-tighter">
          Season {{ season?.name || '…' }} Overview
        </div>
      </div>
      <div class="row items-center q-gutter-x-sm">
        <KennerButton
          v-if="!loading && season"
          flat
          icon="refresh"
          round
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
      <!-- Season Info Section -->
      <div class="row q-col-gutter-md q-mb-lg">
        <div class="col-12 col-md-6">
          <ContentSection
            title="Season Info"
            icon="info"
            color="primary"
            style="margin-top: 0"
            :bordered="false"
          >
            <div class="row q-gutter-sm items-center">
              <q-badge align="middle" color="grey-2" text-color="grey-9" class="q-pa-sm text-weight-bold">
                {{ leagues.length }} leagues
              </q-badge>
              <q-badge
                v-if="seasonStatusLabel"
                :color="statusColor"
                class="q-pa-sm text-weight-bold"
                :label="seasonStatusLabel"
              />
            </div>
          </ContentSection>
        </div>

        <div class="col-12 col-md-6">
          <ContentSection
            title="Season Winners"
            icon="emoji_events"
            color="amber-8"
            style="margin-top: 0"
            :bordered="false"
          >
            <SeasonWinners :season-id="seasonId" />
          </ContentSection>
        </div>
      </div>

      <!-- Leagues Grid -->
      <div class="q-mt-xl">
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

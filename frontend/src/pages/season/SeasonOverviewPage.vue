<template>
  <q-page class="q-pa-md">
    <!-- Header Area -->
    <div class="row items-center justify-between q-mb-md">
      <div class="row items-center q-gutter-x-sm">
        <q-icon name="military_tech" size="md" color="primary" />
        <div class="text-h4 text-weight-bolder text-dark tracking-tighter">
          Manage Season {{ season?.name || '…' }}
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
        <KennerButton
          flat
          icon="close"
          round
          color="grey-7"
          size="md"
          @click="router.back()"
        >
          <KennerTooltip>Back</KennerTooltip>
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
            title="Registered Members"
            icon="people"
            color="secondary"
            style="margin-top: 0"
            :bordered="false"
          >
            <div v-if="participants.length > 0" class="row q-col-gutter-xs">
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
            <div v-else class="text-caption text-grey-6 italic">No registered members for this season.</div>
          </ContentSection>
        </div>
      </div>

      <!-- Leagues Grid -->
      <ContentSection
        title="Leagues"
        icon="groups"
        color="accent"
        :bordered="false"
      >
        <div v-if="leagues.length === 0" class="text-grey-7 q-pa-md bg-grey-1 rounded-borders text-center">
          No leagues found for this season.
        </div>
        <div v-else class="row q-col-gutter-lg">
          <div
            v-for="league in leagues"
            :key="league.id"
            class="col-12 col-sm-6 col-md-4"
          >
            <LeagueList :league="league"/>
          </div>
        </div>
      </ContentSection>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { fetchLeaguesBySeason, fetchSeason, fetchSeasonParticipants } from 'src/services/seasonService';
import LeagueList from 'components/season/LeagueList.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import ContentSection from 'components/base/ContentSection.vue';
import ErrorDisplay from 'components/base/ErrorDisplay.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
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

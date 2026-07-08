<template>
  <q-page class="q-pa-md">
    <!-- Header Area -->
    <div v-if="route.name !== 'league-manager'" class="row items-center justify-between q-mb-md">
      <div class="row items-center q-gutter-x-sm">
        <q-icon name="military_tech" size="md" color="primary" />
        <div class="text-h4 text-weight-bolder text-dark tracking-tighter">
          {{ isAdmin ? 'Manage Season' : 'Season Details' }} {{ season?.name || '…' }}
        </div>
      </div>
      <div class="row items-center q-gutter-x-sm">
        <KennerButton
          flat
          icon="visibility"
          round
          color="secondary"
          size="md"
          :to="{ name: 'season-overview', params: { id: seasonId } }"
        >
          <KennerTooltip>View Public Overview</KennerTooltip>
        </KennerButton>
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
      <router-view v-if="route.name === 'league-manager'" />

      <template v-else>
        <!-- Season Info & Members -->
        <div class="season-summary q-mb-lg">
          <div class="season-summary__header row items-center no-wrap q-gutter-x-sm q-px-md q-py-md">
            <div class="season-summary__icon">
              <q-icon name="groups" size="20px" />
            </div>
            <div class="col">
              <div class="text-subtitle1 text-weight-bolder season-summary__title">Participants</div>
              <div class="text-caption text-grey-6">Overview for this season</div>
            </div>
            <div class="row items-center q-gutter-x-xs">
              <div class="stat-pill">
                <q-icon name="emoji_events" size="14px" class="q-mr-xs" />
                <span>{{ leagues.length }} leagues</span>
              </div>
              <div class="stat-pill">
                <q-icon name="person" size="14px" class="q-mr-xs" />
                <span>{{ participants.length }} participants</span>
              </div>
              <div
                v-if="seasonStatusLabel"
                class="status-pill"
                :class="`status-pill--${statusColor}`"
              >
                {{ seasonStatusLabel }}
              </div>
            </div>
          </div>

          <div class="season-summary__divider" />

          <div class="q-px-md q-pt-sm q-pb-md">
            <div v-if="participants.length > 0" class="row q-col-gutter-xs">
              <div
                v-for="p in participants"
                :key="p.id"
                class="member-chip q-mr-xs q-mb-xs"
              >
                <q-icon name="person" size="14px" class="q-mr-xs" />
                <span>{{ p.profile_name }}</span>
              </div>
            </div>
            <div v-else class="text-caption text-grey-6 italic">No registered users for this season.</div>
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
      </template>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { fetchLeaguesBySeason, fetchSeason, fetchSeasonParticipants } from 'src/services/seasonService';
import LeagueList from 'components/season/LeagueList.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import ContentSection from 'components/base/ContentSection.vue';
import ErrorDisplay from 'components/base/ErrorDisplay.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import { TSeasonDto, TLeagueDto, TSeasonParticipantDto } from 'src/types';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';

const route = useRoute();
const { isAdmin } = storeToRefs(useUserStore());
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

<style scoped lang="scss">
.season-summary {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(54, 64, 88, 0.08);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(54, 64, 88, 0.04);
  overflow: hidden;
}

.season-summary__header {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.6) 0%, rgba(255, 255, 255, 0.2) 100%);
}

.season-summary__title {
  color: #1f2937;
  letter-spacing: -0.2px;
}

.season-summary__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  color: #fff;
  background: linear-gradient(135deg, var(--q-primary) 0%, var(--q-accent) 100%);
  flex: 0 0 auto;
}

.season-summary__divider {
  height: 1px;
  background: linear-gradient(to right, transparent 0%, rgba(54, 64, 88, 0.1) 50%, transparent 100%);
}

.stat-pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(54, 64, 88, 0.06);
  color: #475569;
  font-size: 12px;
  font-weight: 600;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
  border: 1px solid transparent;
  text-transform: uppercase;
}

.status-pill--primary {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0.05) 100%);
  color: var(--q-primary);
  border-color: rgba(99, 102, 241, 0.25);
}

.status-pill--teal-6 {
  background: linear-gradient(135deg, rgba(0, 150, 136, 0.15) 0%, rgba(0, 150, 136, 0.05) 100%);
  color: #00897b;
  border-color: rgba(0, 150, 136, 0.25);
}

.status-pill--grey-7,
.status-pill--grey-6 {
  background: rgba(54, 64, 88, 0.06);
  color: #475569;
  border-color: rgba(54, 64, 88, 0.12);
}

.member-chip {
  display: inline-flex;
  align-items: center;
  padding: 5px 12px;
  border-radius: 999px;
  background: rgba(54, 64, 88, 0.05);
  border: 1px solid rgba(54, 64, 88, 0.06);
  color: #334155;
  font-size: 13px;
  font-weight: 500;
  transition: background 0.2s ease, border-color 0.2s ease, transform 0.2s ease;

  &:hover {
    background: rgba(54, 64, 88, 0.1);
    border-color: rgba(54, 64, 88, 0.12);
    transform: translateY(-1px);
  }
}

:global(.body--dark) .season-summary {
  background: rgba(30, 30, 30, 0.8);
  border-color: rgba(255, 255, 255, 0.08);
}

:global(.body--dark) .season-summary__header {
  background: linear-gradient(135deg, rgba(40, 40, 40, 0.6) 0%, rgba(30, 30, 30, 0.3) 100%);
}

:global(.body--dark) .season-summary__title {
  color: #ececec;
}

:global(.body--dark) .stat-pill {
  background: rgba(255, 255, 255, 0.08);
  color: #cbd5e1;
}

:global(.body--dark) .member-chip {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.08);
  color: #e2e8f0;

  &:hover {
    background: rgba(255, 255, 255, 0.12);
    border-color: rgba(255, 255, 255, 0.16);
  }
}
</style>

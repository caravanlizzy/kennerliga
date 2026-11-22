<template>
  <div class="q-pa-md max-width-container">
    <div v-if="loading" class="q-py-xl text-center">
      <q-spinner-dots color="primary" size="40px" />
    </div>

    <div v-else-if="error || !selectedGame" class="q-py-md">
      <q-banner rounded dense class="bg-red-1 text-negative">
        <template #avatar><q-icon name="warning" color="negative" /></template>
        {{ error || 'Match result not found.' }}
      </q-banner>
    </div>

    <div v-else class="column q-gutter-y-lg">
      <!-- Header Card -->
      <q-card flat class="kenner-detail-card">
        <q-card-section class="q-pa-lg">
          <div class="row items-start justify-between q-col-gutter-md">
            <div>
              <div class="row items-center q-gutter-x-sm q-mb-xs">
                <q-badge color="primary" text-color="white" class="q-px-sm">
                  {{
                    selectedGame.season_name ||
                    (selectedGame.season_id
                      ? `Season #${selectedGame.season_id}`
                      : 'Season')
                  }}
                </q-badge>
                <q-badge
                  v-if="selectedGame.league_level != null"
                  color="secondary"
                  text-color="white"
                  class="q-px-sm"
                >
                  League {{ selectedGame.league_level }}
                </q-badge>
                <q-badge
                  v-if="hasRecord"
                  color="deep-orange-1"
                  text-color="deep-orange-9"
                  class="q-px-sm text-weight-bolder"
                >
                  <q-icon
                    name="local_fire_department"
                    size="14px"
                    class="q-mr-xs text-deep-orange-6"
                  />
                  RECORD SCORE
                </q-badge>
                <q-badge
                  v-if="selectedGame.platform_name"
                  color="grey-3"
                  text-color="grey-8"
                  class="q-px-sm"
                >
                  {{ selectedGame.platform_name }}
                </q-badge>
              </div>

              <h1 class="text-h4 text-weight-bolder text-grey-9 q-my-xs">
                {{ selectedGame.game_name || `Game #${selectedGame.game}` }}
              </h1>
            </div>

            <!-- Actions -->
            <div class="row items-center q-gutter-sm">
              <KennerButton
                v-if="selectedGame.game"
                outline
                no-caps
                color="primary"
                icon="sports_esports"
                label="Game Stats"
                @click="
                  router.push({
                    name: 'game-detail',
                    params: { id: selectedGame.game },
                  })
                "
              />
              <!-- Edit Button for Admins -->
              <KennerButton
                v-if="isAdmin"
                outline
                no-caps
                color="secondary"
                icon="edit"
                label="Edit Result"
                :loading="actionLoading"
                @click="openEditDialog"
              />
            </div>
          </div>

          <!-- Selected Game Options -->
          <div
            v-if="
              selectedGame.selected_options &&
              selectedGame.selected_options.length > 0
            "
            class="row items-center q-gutter-xs q-mt-sm"
          >
            <span class="text-caption text-grey-7 text-weight-medium q-mr-xs"
              >Options:</span
            >
            <q-chip
              v-for="opt in selectedGame.selected_options"
              :key="opt.id"
              dense
              size="sm"
              color="grey-2"
              text-color="grey-8"
            >
              <span class="text-weight-bold q-mr-xs"
                >{{ opt.game_option?.name }}:</span
              >
              <span>{{ opt.choice?.name || (opt.value ? 'Yes' : 'No') }}</span>
            </q-chip>
          </div>
        </q-card-section>
      </q-card>

      <!-- Match Results Section -->
      <ContentSection
        title="Scoreboard & Standings"
        color="primary"
        icon="emoji_events"
        flat
        no-margin
      >
        <MatchResult :selectedGame="selectedGame" :displayGameName="false" />
      </ContentSection>
    </div>

    <!-- Edit Dialog (same as Manage League) -->
    <ManagerFormsDialog
      v-if="league && activeForm"
      :league="league"
      :activeForm="activeForm"
      @close="activeForm = null"
      @success="onEditSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { storeToRefs } from 'pinia';
import { useUserStore } from 'stores/userStore';
import { fetchSelectedGameById } from 'src/services/gameService';
import { fetchLeagueDetails } from 'src/services/leagueService';
import ContentSection from 'components/base/ContentSection.vue';
import KennerButton from 'components/base/KennerButton.vue';
import MatchResult from 'components/league/MatchResult.vue';
import ManagerFormsDialog, {
  type TActiveForm,
} from 'components/league/manager/ManagerFormsDialog.vue';
import type { TSelectedGameDto, TLeagueDto } from 'src/types';

const route = useRoute();
const router = useRouter();
const $q = useQuasar();
const userStore = useUserStore();
const { isAdmin } = storeToRefs(userStore);

const selectedGame = ref<TSelectedGameDto | null>(null);
const league = ref<TLeagueDto | null>(null);
const loading = ref(true);
const actionLoading = ref(false);
const error = ref<string | null>(null);
const activeForm = ref<TActiveForm | null>(null);

const gameId = computed(() => Number(route.params.id));
const hasRecord = computed(
  () => selectedGame.value?.results?.some((r) => r.is_record) ?? false
);

async function loadData() {
  if (isNaN(gameId.value)) {
    error.value = 'Invalid match result ID.';
    loading.value = false;
    return;
  }

  loading.value = true;
  error.value = null;
  try {
    const gameData = await fetchSelectedGameById(gameId.value);
    selectedGame.value = gameData;
    if (gameData.league) {
      league.value = await fetchLeagueDetails(gameData.league);
    }
  } catch (err: unknown) {
    console.error('Failed to load match result details:', err);
    error.value = 'Failed to load match result details.';
  } finally {
    loading.value = false;
  }
}

async function openEditDialog() {
  if (!selectedGame.value) return;

  if (!league.value && selectedGame.value.league) {
    actionLoading.value = true;
    try {
      league.value = await fetchLeagueDetails(selectedGame.value.league);
    } catch (err) {
      console.error('Failed to load league for edit:', err);
      $q.notify({
        type: 'negative',
        message: 'Could not load league data for editing.',
      });
      actionLoading.value = false;
      return;
    }
    actionLoading.value = false;
  }

  activeForm.value = {
    type: 'post-result',
    selGame: selectedGame.value,
  };
}

async function onEditSuccess() {
  activeForm.value = null;
  $q.notify({
    type: 'positive',
    message: 'Match result updated successfully.',
  });
  await loadData();
}

onMounted(() => {
  loadData();
});
</script>

<style scoped lang="scss">
.max-width-container {
  max-width: 1000px;
  margin: 0 auto;
}

.kenner-detail-card {
  background: var(--kenner-bg-glass-card);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--kenner-border-color);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(54, 64, 88, 0.04);
}
</style>

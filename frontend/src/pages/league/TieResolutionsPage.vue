<template>
  <q-page class="q-py-md flex justify-center">
    <div
      style="max-width: var(--kenner-max-width-text); width: 100%"
      class="q-px-sm"
    >
      <!-- Header Hero Card -->
      <div
        class="management-hero-card q-pa-lg q-mb-lg row items-center justify-between"
      >
        <div class="column">
          <div class="row items-center q-gutter-x-sm q-mb-xs">
            <q-icon name="balance" color="primary" size="32px" />
            <div class="text-h5 text-weight-bold text-dark tracking-tight">
              Tie Resolutions
            </div>
          </div>
          <div class="text-caption text-grey-7">
            Inspect, modify player orders, or remove tie-breaker decisions across leagues.
          </div>
        </div>
      </div>

      <!-- Filters & Stats -->
      <q-card flat class="management-card q-mb-lg">
        <q-card-section class="q-pa-md">
          <div class="row q-col-gutter-sm items-center">
            <div class="col-12 col-sm-6 col-md-4">
              <KennerSelect
                v-model="selectedSeasonId"
                :options="seasonOptions"
                label="Filter by Season"
                emit-value
                map-options
                clearable
                dense
              />
            </div>
            <div class="col-12 col-sm-6 col-md-5">
              <KennerInput
                v-model="searchQuery"
                label="Search by player or note"
                dense
                clearable
              >
                <template #append>
                  <q-icon name="search" />
                </template>
              </KennerInput>
            </div>
            <div class="col-12 col-md-3 row items-center justify-end q-gutter-x-sm">
              <q-badge color="primary" rounded class="q-px-sm q-py-xs">
                {{ filteredResolutions.length }} Resolved
              </q-badge>
              <KennerButton
                flat
                round
                dense
                icon="refresh"
                color="grey-7"
                :loading="loading"
                @click="loadResolutions"
              />
            </div>
          </div>
        </q-card-section>
      </q-card>

      <!-- Loading State -->
      <div v-if="loading" class="flex flex-center q-my-xl">
        <LoadingSpinner />
      </div>

      <!-- Empty State -->
      <q-card
        v-else-if="filteredResolutions.length === 0"
        flat
        class="management-card q-pa-xl text-center column items-center"
      >
        <q-icon name="balance" size="48px" class="opacity-30 q-mb-sm text-grey-6" />
        <div class="text-subtitle1 text-weight-medium text-grey-8">
          No tie resolutions found
        </div>
        <div class="text-caption text-grey-6 q-mt-xs">
          When ties are resolved by players or admins, they will appear here.
        </div>
      </q-card>

      <!-- Resolutions List -->
      <div v-else class="column q-gutter-y-md">
        <q-card
          v-for="res in filteredResolutions"
          :key="res.id"
          flat
          class="management-card"
        >
          <q-card-section class="q-pa-md">
            <!-- Card Header -->
            <div class="row items-center justify-between q-mb-sm">
              <div class="row items-center q-gutter-x-sm">
                <q-chip
                  square
                  color="grey-2"
                  text-color="grey-9"
                  class="text-weight-bold"
                  icon="event"
                  size="sm"
                >
                  {{ res.season_name || `Season #${res.season_id}` }}
                </q-chip>
                <LeagueLevel
                  badge
                  :level="res.league_level"
                  class="q-pa-xs"
                />
                <q-badge
                  color="positive"
                  outline
                  class="text-weight-bold q-px-xs"
                >
                  {{ res.reason_display || res.reason }}
                </q-badge>
              </div>

              <div class="text-caption text-grey-6">
                {{ formatDate(res.updated_at || res.created_at) }}
              </div>
            </div>

            <!-- Ordered Players List -->
            <div class="q-my-sm">
              <div class="text-caption text-grey-7 text-weight-medium q-mb-xs">
                Resolved Player Order:
              </div>
              <q-list bordered separator class="rounded-borders bg-white">
                <q-item
                  v-for="(entry, idx) in res.entries"
                  :key="entry.id || entry.player_profile_id"
                  dense
                  class="q-py-xs"
                >
                  <q-item-section avatar style="min-width: 32px">
                    <q-badge
                      :color="idx === 0 ? 'amber-9' : 'primary'"
                      text-color="white"
                      :label="idx + 1"
                    />
                  </q-item-section>
                  <q-item-section avatar style="min-width: 36px">
                    <UserAvatar
                      :display-username="entry.username || entry.profile_name"
                      :navigation-name="entry.username || undefined"
                      :subtitle="
                        entry.profile_name !== entry.username
                          ? entry.profile_name
                          : undefined
                      "
                      :shape="entry.avatar_shape"
                      :color="entry.avatar_color"
                      size="28px"
                    />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label class="text-weight-medium">
                      {{ entry.profile_name }}
                    </q-item-label>
                    <q-item-label v-if="entry.username" caption class="text-grey-6">
                      @{{ entry.username }}
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <!-- Note if present -->
            <div
              v-if="res.note"
              class="q-mt-sm q-pa-sm bg-grey-1 rounded-borders row items-start q-gutter-x-xs"
            >
              <q-icon name="sticky_note_2" color="grey-6" size="16px" class="q-mt-xs" />
              <div class="col text-caption text-grey-8">
                <span class="text-weight-bold">Note:</span> {{ res.note }}
              </div>
            </div>

            <!-- Card Actions -->
            <div class="row justify-end q-gutter-x-sm q-mt-sm">
              <KennerButton
                label="Edit Order & Reason"
                size="sm"
                color="primary"
                outline
                no-caps
                icon="edit"
                @click="openEditDialog(res)"
              />
              <KennerButton
                label="Delete"
                size="sm"
                color="negative"
                outline
                no-caps
                icon="delete"
                @click="openDeleteDialog(res)"
              />
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Edit Dialog -->
      <q-dialog v-model="showEditDialog" persistent>
        <q-card
          style="min-width: 320px; max-width: 520px; width: 100%; border-radius: 16px"
        >
          <q-card-section class="row items-center justify-between q-pb-none">
            <div class="text-subtitle1 text-weight-bold">Edit Tie Resolution</div>
            <q-btn icon="close" flat round dense v-close-popup />
          </q-card-section>
          <q-card-section>
            <ResolveTieForm
              v-if="editingResolution"
              :league-id="editingResolution.league"
              :group-key="editingResolution.group_key"
              :members="editingResolution.entries"
              :initial-reason="editingResolution.reason"
              :initial-note="editingResolution.note"
              :resolution-id="editingResolution.id"
              @on-success="onEditSuccess"
            />
          </q-card-section>
        </q-card>
      </q-dialog>

      <!-- Delete Confirmation Dialog -->
      <q-dialog v-model="showDeleteDialog">
        <q-card style="min-width: 300px; max-width: 440px; border-radius: 16px">
          <q-card-section class="row items-center q-pb-none">
            <div class="row items-center q-gutter-x-sm text-negative">
              <q-icon name="warning" size="24px" />
              <div class="text-subtitle1 text-weight-bold text-dark">
                Delete Tie Resolution?
              </div>
            </div>
          </q-card-section>
          <q-card-section class="text-body2 text-grey-8">
            Are you sure you want to delete this tie resolution?
            The standings for this league will revert to an unresolved tie.
          </q-card-section>
          <q-card-actions align="right" class="q-pa-md">
            <KennerButton label="Cancel" flat color="grey-7" v-close-popup />
            <KennerButton
              label="Delete"
              color="negative"
              :loading="deleting"
              @click="confirmDelete"
            />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import KennerButton from 'components/base/KennerButton.vue';
import KennerInput from 'components/base/KennerInput.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import UserAvatar from 'components/ui/UserAvatar.vue';
import LeagueLevel from 'components/season/LeagueLevel.vue';
import ResolveTieForm from 'components/league/manager/ResolveTieForm.vue';
import {
  fetchTieResolutions,
  deleteTieResolution,
} from 'src/services/leagueService';
import { fetchSeasons } from 'src/services/seasonService';
import type { TLeagueTieResolutionDto, TSeasonDto } from 'src/types';
import { formatDateTime } from 'src/helpers';

const $q = useQuasar();

const resolutions = ref<TLeagueTieResolutionDto[]>([]);
const seasons = ref<TSeasonDto[]>([]);
const loading = ref(false);
const deleting = ref(false);

const selectedSeasonId = ref<number | null>(null);
const searchQuery = ref('');

const showEditDialog = ref(false);
const editingResolution = ref<TLeagueTieResolutionDto | null>(null);

const showDeleteDialog = ref(false);
const resolutionToDelete = ref<TLeagueTieResolutionDto | null>(null);

const seasonOptions = computed(() => {
  return seasons.value.map((s) => ({
    label: s.name,
    value: s.id,
  }));
});

const formatDate = (val?: string): string => {
  if (!val) return '';
  return formatDateTime(val);
};

const loadResolutions = async () => {
  loading.value = true;
  try {
    resolutions.value = await fetchTieResolutions();
  } catch (e) {
    console.error('Error fetching tie resolutions:', e);
    $q.notify({
      type: 'negative',
      message: 'Failed to load tie resolutions',
    });
  } finally {
    loading.value = false;
  }
};

const loadSeasons = async () => {
  try {
    const list = await fetchSeasons();
    seasons.value = list || [];
  } catch (e) {
    console.error('Error fetching seasons:', e);
  }
};

const filteredResolutions = computed(() => {
  return resolutions.value.filter((r) => {
    if (selectedSeasonId.value && r.season_id !== selectedSeasonId.value) {
      return false;
    }
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase().trim();
      const inEntries = (r.entries || []).some(
        (e) =>
          e.profile_name?.toLowerCase().includes(q) ||
          e.username?.toLowerCase().includes(q)
      );
      const inReason =
        r.reason?.toLowerCase().includes(q) ||
        r.reason_display?.toLowerCase().includes(q);
      const inNote = r.note?.toLowerCase().includes(q);
      const inSeason = r.season_name?.toLowerCase().includes(q);
      if (!inEntries && !inReason && !inNote && !inSeason) {
        return false;
      }
    }
    return true;
  });
});

const openEditDialog = (res: TLeagueTieResolutionDto) => {
  editingResolution.value = res;
  showEditDialog.value = true;
};

const onEditSuccess = async () => {
  showEditDialog.value = false;
  editingResolution.value = null;
  await loadResolutions();
};

const openDeleteDialog = (res: TLeagueTieResolutionDto) => {
  resolutionToDelete.value = res;
  showDeleteDialog.value = true;
};

const confirmDelete = async () => {
  if (!resolutionToDelete.value) return;
  deleting.value = true;
  try {
    await deleteTieResolution(resolutionToDelete.value.id);
    $q.notify({
      type: 'positive',
      message: 'Tie resolution deleted. League tie is now unresolved.',
    });
    showDeleteDialog.value = false;
    resolutionToDelete.value = null;
    await loadResolutions();
  } catch (e) {
    console.error('Error deleting tie resolution:', e);
    $q.notify({
      type: 'negative',
      message: 'Failed to delete tie resolution',
    });
  } finally {
    deleting.value = false;
  }
};

onMounted(async () => {
  await Promise.all([loadResolutions(), loadSeasons()]);
});
</script>

<style scoped lang="scss">
.management-hero-card {
  background: var(--kenner-card-bg, #ffffff);
  border-radius: var(--kenner-card-radius, 16px);
  border: 1px solid var(--kenner-border-subtle, rgba(0, 0, 0, 0.08));
}

.management-card {
  background: var(--kenner-card-bg, #ffffff);
  border-radius: var(--kenner-card-radius, 12px);
  border: 1px solid var(--kenner-border-subtle, rgba(0, 0, 0, 0.08));
}
</style>

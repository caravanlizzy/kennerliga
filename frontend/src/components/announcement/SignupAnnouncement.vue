<template>
  <q-card
    flat
    class="announcement-card overflow-hidden announcement-card--signup"
    :class="{ 'no-border-radius': shouldRemoveBorders, 'announcement-card--minimized': isMinimized }"
  >
    <!-- Minimized View -->
    <q-card-section
      v-if="isMinimized"
      class="q-py-sm row items-center no-wrap signup-minimized"
      @click="toggleMinimized"
    >
      <q-icon name="how_to_reg" size="20px" color="accent" class="q-mr-sm" />
      <div class="text-subtitle2 text-weight-bolder text-primary col ellipsis">
        {{ announcement.title }}
      </div>
      <div
        v-if="isSignedUpForOpenSeason"
        class="row items-center q-gutter-x-xs text-positive text-weight-bold text-caption q-mr-sm"
      >
        <q-icon name="check_circle" size="14px" />
        <span>Signed up</span>
      </div>
      <div
        v-else
        class="row items-center q-gutter-x-xs text-negative text-weight-bold text-caption q-mr-sm"
      >
        <q-icon name="radio_button_unchecked" size="14px" />
        <span>Not signed up</span>
      </div>
      <q-btn
        flat
        dense
        round
        icon="expand_more"
        size="sm"
        color="grey-7"
        @click.stop="toggleMinimized"
      >
        <q-tooltip>Expand</q-tooltip>
      </q-btn>
    </q-card-section>

    <q-card-section
      v-else
      :class="[
        isMobile ? 'q-py-md' : 'q-py-lg',
        'relative-position row items-center no-wrap signup-content',
      ]"
    >
      <!-- Minimize Button -->
      <q-btn
        flat
        dense
        round
        icon="expand_less"
        size="sm"
        color="grey-7"
        class="absolute minimize-btn content-layer"
        @click="toggleMinimized"
      >
        <q-tooltip>Minimize</q-tooltip>
      </q-btn>
      <!-- Background Ornament -->
      <div class="signup-ornament absolute-right overflow-hidden">
        <q-icon name="campaign" size="180px" color="accent" />
      </div>

      <!-- Content Header (Icon + Text) -->
      <div class="row items-center no-wrap col q-px-md content-layer">
              <!-- Icon Circle -->
              <div
                class="icon-wrapper flex flex-center q-mr-lg"
                :class="[isMobile ? 'icon-wrapper--mobile' : '']"
              >
                <q-icon
                  name="how_to_reg"
                  :size="isMobile ? '32px' : '40px'"
                  color="white"
                />
              </div>

        <!-- Content -->
        <div class="col">
          <!-- Header & Actions -->
          <div class="row items-center justify-between no-wrap q-mb-xs">
            <div class="text-h6 text-weight-bolder lh-tight text-primary col">
              {{ announcement.title }}
            </div>

            <!-- Mobile Action Button -->
            <div v-if="isMobile" class="col-auto">
              <KennerButton
                v-if="!isSignedUpForOpenSeason"
                unelevated
                dense
                no-caps
                color="primary"
                class="q-px-md"
                @click="signUp"
              >
                Sign up
                <KennerTooltip v-if="!isAuthenticated" class="bg-grey-9">
                  Login to sign up for upcoming season
                </KennerTooltip>
              </KennerButton>

              <div
                v-else
                class="row items-center q-gutter-x-xs text-positive text-weight-bold text-caption"
              >
                <q-icon name="check_circle" size="16px" />
                <span>Signed up</span>
              </div>
            </div>
          </div>

          <div
            v-if="announcement.content"
            class="text-subtitle2 text-grey-8 q-mb-sm"
          >
            {{ announcement.content }}
          </div>

          <!-- Integrated Participants List -->
          <div :class="isMobile ? 'q-mt-sm' : 'q-mt-lg'">
            <div class="row items-center q-gutter-x-sm" :class="isMobile ? 'q-mb-xs' : 'q-mb-sm'">
              <div
                class="text-caption text-weight-bolder text-grey-8 uppercase tracking-widest"
                :style="isMobile ? 'font-size: 0.6rem' : 'font-size: 0.65rem'"
              >
                Signed up
              </div>
              <q-badge
                color="accent"
                :label="activeParticipants.length"
                rounded
                class="text-weight-bold"
                :style="isMobile ? 'font-size: 9px; padding: 1px 4px' : 'font-size: 10px; padding: 2px 6px'"
              />
            </div>

            <div v-if="participantsLoading" class="row q-gutter-xs">
              <q-skeleton
                v-for="i in 5"
                :key="i"
                type="rect"
                :width="isMobile ? '40px' : '60px'"
                :height="isMobile ? '20px' : '28px'"
                class="rounded-borders"
              />
            </div>
            <template v-else-if="participantsLoaded">
              <div v-if="activeParticipants.length">
                <!-- Grouped by projected league -->
                <div
                  v-for="group in projectedLeagueGroups"
                  :key="`L-${group.level}`"
                  :class="isMobile ? 'q-mb-sm' : 'q-mb-md'"
                >
                  <div class="row items-center q-gutter-x-xs q-mb-xs">
                    <div
                      class="text-caption text-weight-bolder text-grey-7 uppercase tracking-widest"
                      :style="isMobile ? 'font-size: 0.55rem' : 'font-size: 0.6rem'"
                    >
                      League {{ group.level }}
                    </div>
                    <q-badge
                      color="grey-5"
                      :label="`${group.members.length}/${group.size}`"
                      rounded
                      class="text-weight-bold"
                      :style="isMobile ? 'font-size: 9px; padding: 1px 4px' : 'font-size: 10px; padding: 2px 6px'"
                    />
                  </div>
                  <div class="row q-gutter-xs">
                    <div v-for="(p, index) in group.members" :key="p.profile || index" class="col-auto">
                      <div class="participant-chip" :class="{ 'participant-chip--mobile': isMobile }">
                        {{ p.profile_name || 'Anonymous' }}
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Shuffle pool -->
                <div v-if="shufflePool.length" :class="isMobile ? 'q-mt-sm' : 'q-mt-md'">
                  <div class="row items-center q-gutter-x-xs q-mb-xs">
                    <div
                      class="text-caption text-weight-bolder text-grey-7 uppercase tracking-widest"
                      :style="isMobile ? 'font-size: 0.55rem' : 'font-size: 0.6rem'"
                    >
                      Shuffle pool
                    </div>
                    <q-badge
                      color="warning"
                      :label="shufflePool.length"
                      rounded
                      class="text-weight-bold"
                      :style="isMobile ? 'font-size: 9px; padding: 1px 4px' : 'font-size: 10px; padding: 2px 6px'"
                    />
                    <q-icon name="shuffle" size="12px" class="text-grey-6" />
                  </div>
                  <div class="row q-gutter-xs">
                    <div v-for="(p, index) in shufflePool" :key="p.profile || index" class="col-auto">
                      <div
                        class="participant-chip participant-chip--shuffle"
                        :class="{ 'participant-chip--mobile': isMobile }"
                      >
                        {{ p.profile_name || 'Anonymous' }}
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Fallback: signed-up users not yet in projection (e.g. just registered) -->
                <div v-if="unprojectedParticipants.length" :class="isMobile ? 'q-mt-sm' : 'q-mt-md'">
                  <div class="row q-gutter-xs">
                    <div v-for="(p, index) in unprojectedParticipants" :key="p.id || index" class="col-auto">
                      <div class="participant-chip" :class="{ 'participant-chip--mobile': isMobile }">
                        {{ p.profile_name || 'Anonymous' }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="text-caption text-grey-6 italic">
                {{ isAuthenticated ? 'Nobody signed up yet. Be the first!' : 'Nobody signed up yet.' }}
              </div>

              <!-- Missing Participants -->
              <div v-if="missingParticipants.length" class="q-mt-md">
                <div class="row items-center q-gutter-x-sm q-mb-xs">
                  <div
                    class="text-caption text-weight-bolder text-grey-6 uppercase tracking-widest"
                    :style="isMobile ? 'font-size: 0.55rem' : 'font-size: 0.6rem'"
                  >
                    Missing from previous season
                  </div>
                </div>
                <div class="row q-gutter-xs">
                  <div v-for="(p, index) in missingParticipants" :key="p.id || index" class="col-auto">
                    <div
                      class="participant-chip participant-chip--missing"
                      :class="{ 'participant-chip--mobile': isMobile }"
                    >
                      <q-icon name="history" size="12px" class="q-mr-xs" />
                      {{ p.profile_name || 'Anonymous' }}
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- Actions (Desktop all) -->
      <div class="row items-center q-gutter-sm absolute-top-right q-pa-md content-layer">
        <template v-if="!isMobile">
          <KennerButton
            v-if="!isSignedUpForOpenSeason"
            unelevated
            dense
            no-caps
            color="primary"
            class="q-px-md"
            @click="signUp"
          >
            Sign up
            <KennerTooltip v-if="!isAuthenticated" class="bg-grey-9">
              Login to sign up for upcoming season
            </KennerTooltip>
          </KennerButton>

          <div
            v-else
            class="row items-center q-gutter-x-xs text-positive text-weight-bold text-caption q-px-sm"
          >
            <q-icon name="check_circle" size="16px" />
            <span>Signed up</span>
          </div>
        </template>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { ref, onMounted, computed } from 'vue';
import { useUserStore } from 'stores/userStore';
import { useResponsive } from 'src/composables/responsive';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import { useQuasar } from 'quasar';
import {
  fetchRegistrationStatus,
  fetchOpenSeasonParticipants,
  fetchSeasonParticipants,
  fetchProjectedLeagues,
  registerForSeason,
} from 'src/services/seasonService';
import type {
  TProjectedLeague,
  TProjectedLeagueMember,
} from 'src/services/seasonService';
import type { TAnnouncementDto, TSeasonParticipantDto } from 'src/types';

const props = defineProps<{
  announcement: TAnnouncementDto & { season_id?: number };
}>();

const { announcement } = props;

const $q = useQuasar();
const { isMobile } = useResponsive();

const shouldRemoveBorders = ref($q.screen.lt.sm);

const userStore = useUserStore();
const { isAuthenticated } = storeToRefs(userStore);

const isSignedUpForOpenSeason = ref(false);
const openSeasonId = ref<number | null>(null);
const participants = ref<TSeasonParticipantDto[] | null>(null);
const participantsLoading = ref(false);
const participantsLoaded = ref(false);
const projectedLeagues = ref<TProjectedLeague[]>([]);

const minimizedStorageKey = computed(() => {
  const sid = announcement.season_id || openSeasonId.value;
  return sid ? `signup-announcement-minimized:${sid}` : null;
});

const isMinimized = ref(false);

function toggleMinimized() {
  isMinimized.value = !isMinimized.value;
  const key = minimizedStorageKey.value;
  if (key) {
    try {
      if (isMinimized.value) {
        localStorage.setItem(key, '1');
      } else {
        localStorage.removeItem(key);
      }
    } catch {
      // ignore localStorage errors
    }
  }
}
const shufflePool = ref<TProjectedLeagueMember[]>([]);

const activeParticipants = computed(() => {
  return (participants.value || []).filter((p) => !p.is_prev_unregistered);
});

const missingParticipants = computed(() => {
  return (participants.value || []).filter((p) => p.is_prev_unregistered);
});

const projectedLeagueGroups = computed<TProjectedLeague[]>(() => {
  return (projectedLeagues.value || []).filter((g) => g.members && g.members.length > 0);
});

// Profile ids that appear anywhere in the projection (leagues or shuffle pool)
const projectedProfileIds = computed<Set<number>>(() => {
  const ids = new Set<number>();
  for (const g of projectedLeagues.value || []) {
    for (const m of g.members || []) ids.add(m.profile);
  }
  for (const m of shufflePool.value || []) ids.add(m.profile);
  return ids;
});

// Signed-up participants not yet reflected by the projection (kept as a flat fallback)
const unprojectedParticipants = computed(() => {
  const known = projectedProfileIds.value;
  return activeParticipants.value.filter((p) => !known.has(p.profile));
});

async function loadParticipants() {
  if (participantsLoading.value) return;
  participantsLoading.value = true;
  try {
    const seasonId = announcement.season_id || openSeasonId.value;
    if (seasonId) {
      // Include previous-season unregistered players for announcement context
      participants.value = await fetchSeasonParticipants(seasonId, { includePrevUnregistered: true });
    } else {
      participants.value = await fetchOpenSeasonParticipants(true);
    }
    await loadProjectedLeagues();
  } catch {
    participants.value = [];
  } finally {
    participantsLoading.value = false;
    participantsLoaded.value = true;
  }
}

async function loadProjectedLeagues() {
  try {
    const seasonId = announcement.season_id || openSeasonId.value || undefined;
    const proj = await fetchProjectedLeagues(seasonId);
    projectedLeagues.value = proj.leagues;
    shufflePool.value = proj.shuffle_pool;
  } catch {
    projectedLeagues.value = [];
    shufflePool.value = [];
  }
}

async function signUp() {
  const seasonId = announcement.season_id || openSeasonId.value;
  if (!seasonId) {
    console.error('No season_id found in announcement or open season');
    return;
  }
  const res = await registerForSeason(seasonId);
  if (res && res.status === 200) {
    isSignedUpForOpenSeason.value = true;
    await loadParticipants();
  }
}

onMounted(async () => {
  const status = await fetchRegistrationStatus();
  openSeasonId.value = status.season_id;
  if (isAuthenticated.value) {
    isSignedUpForOpenSeason.value = status.registered;
  }
  // Restore minimized state from localStorage for the current season
  const key = minimizedStorageKey.value;
  if (key) {
    try {
      isMinimized.value = localStorage.getItem(key) === '1';
    } catch {
      // ignore
    }
  }
  await loadParticipants();
});
</script>

<style scoped>
.announcement-card {
  border-radius: 16px;
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.08);
  width: 100%;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.announcement-card--signup {
  border-top: 4px solid var(--q-accent);
  background: linear-gradient(135deg, rgba($accent, 0.03) 0%, white 100%);
  position: relative;
}

.signup-ornament {
  opacity: 0.03;
  pointer-events: none;
  transform: rotate(-15deg) translateY(10%);
  z-index: 0;
}

.content-layer {
  z-index: 1;
}

.no-border-radius {
  border-radius: 0 !important;
}

.announcement-card:hover:not(.no-border-radius) {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 20px;
  flex-shrink: 0;
  background: var(--q-accent);
  box-shadow: 0 8px 16px rgba($accent, 0.25);
  animation: pulse-shadow 3s infinite;
}

@keyframes pulse-shadow {
  0% { box-shadow: 0 8px 16px rgba($accent, 0.25); }
  50% { box-shadow: 0 8px 24px rgba($accent, 0.4); }
  100% { box-shadow: 0 8px 16px rgba($accent, 0.25); }
}

.icon-wrapper--mobile {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  margin-right: 16px !important;
}

.lh-tight {
  line-height: 1.2;
}

.participant-chip {
  font-size: 12px;
  background: rgba(248, 249, 250, 0.7);
  padding: 4px 12px;
  border-radius: 8px;
  color: #2c3e50;
  font-weight: 600;
  border: 1px solid rgba($accent, 0.1);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.participant-chip--missing {
  background: rgba(0, 0, 0, 0.02);
  color: #777;
  border: 1px dashed rgba(0, 0, 0, 0.15);
  font-weight: 500;
  box-shadow: none;
}

.participant-chip--shuffle {
  background: rgba(255, 193, 7, 0.08);
  color: #8a6d00;
  border: 1px dashed rgba(255, 193, 7, 0.55);
  box-shadow: none;
}

.opacity-60 {
  opacity: 0.6;
}

.participant-chip--mobile {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 6px;
}

.tracking-widest {
  letter-spacing: 0.1em;
}

.minimize-btn {
  top: 4px;
  right: 4px;
  z-index: 2;
}

.signup-minimized {
  cursor: pointer;
}

.announcement-card--minimized {
  border-top-width: 4px;
  border-top-color: var(--q-accent) !important;
}
</style>

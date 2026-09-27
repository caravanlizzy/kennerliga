<template>
  <q-card
    flat
    class="announcement-card overflow-hidden announcement-card--signup"
    :class="{ 'no-border-radius-mobile': shouldRemoveBorders, 'announcement-card--minimized': isMinimized }"
  >
    <!-- Minimized View -->
    <q-card-section
      v-if="isMinimized"
      class="q-py-sm q-px-md row items-center no-wrap signup-minimized"
      @click="toggleMinimized"
    >
      <div class="row items-center no-wrap col min-width-0 q-mr-sm">
        <q-icon name="person_add" size="20px" color="accent" class="q-mr-sm flex-shrink-0" />
        <div class="text-subtitle2 text-weight-bolder text-primary ellipsis">
          {{ announcement.title }}
        </div>
      </div>

      <div class="row items-center no-wrap q-gutter-x-sm flex-shrink-0">
        <div
          v-if="isSignedUpForOpenSeason"
          class="row items-center q-gutter-x-xs text-positive text-weight-bold text-caption"
        >
          <q-icon name="check_circle" size="14px" />
          <span class="gt-xs">Signed up</span>
        </div>
        <div
          v-else
          class="row items-center q-gutter-x-xs text-negative text-weight-bold text-caption"
        >
          <q-icon name="radio_button_unchecked" size="14px" />
          <span class="gt-xs">Not signed up</span>
        </div>
        <q-btn
          flat
          dense
          round
          icon="expand_more"
          size="sm"
          color="grey-7"
          aria-label="Expand"
          @click.stop="toggleMinimized"
        >
          <q-tooltip>Expand</q-tooltip>
        </q-btn>
      </div>
    </q-card-section>

    <!-- Expanded View -->
    <q-card-section
      v-else
      :class="[
        isMobile ? 'q-pa-md' : 'q-pa-lg',
        'relative-position signup-content',
      ]"
    >
      <!-- Background Ornament -->
      <div class="signup-ornament absolute-right overflow-hidden">
        <q-icon name="campaign" size="180px" color="accent" />
      </div>

      <!-- Top Row: Icon + Title & Actions -->
      <div class="row items-start no-wrap content-layer q-mb-md">
        <!-- Icon Circle -->
        <div
          class="icon-wrapper flex flex-center q-mr-md"
          :class="[isMobile ? 'icon-wrapper--mobile' : '']"
        >
          <q-icon
            name="person_add"
            :size="isMobile ? '28px' : '36px'"
            color="white"
          />
        </div>

        <!-- Title and Subtitle / Content -->
        <div class="col min-width-0 q-mr-sm">
          <div class="text-h6 text-weight-bolder lh-tight text-primary q-mb-xs">
            {{ announcement.title }}
          </div>
          <div
            v-if="announcement.content"
            class="text-subtitle2 text-grey-8"
          >
            {{ announcement.content }}
          </div>
        </div>

        <!-- Top Right Actions: Sign up button / status & minimize toggle -->
        <div class="row items-center no-wrap q-gutter-x-xs flex-shrink-0">
          <KennerButton
            v-if="!isSignedUpForOpenSeason"
            unelevated
            dense
            no-caps
            color="accent"
            class="q-px-sm text-weight-bold"
            @click="signUp"
          >
            Sign up
            <KennerTooltip v-if="!isAuthenticated" class="bg-grey-9">
              Login to sign up for upcoming season
            </KennerTooltip>
          </KennerButton>

          <div
            v-else
            class="row items-center q-gutter-x-xs text-positive text-weight-bold text-caption q-px-xs"
          >
            <q-icon name="check_circle" size="16px" />
            <span class="gt-xs">Signed up</span>
          </div>

          <q-btn
            flat
            dense
            round
            icon="expand_less"
            size="sm"
            color="grey-7"
            aria-label="Minimize"
            class="q-ml-xs"
            @click="toggleMinimized"
          >
            <q-tooltip>Minimize</q-tooltip>
          </q-btn>
        </div>
      </div>

      <!-- Integrated Participants & Provisional Leagues List -->
      <div class="content-layer q-mt-md">
        <div class="row items-center q-gutter-x-sm q-mb-sm">
          <div class="text-caption text-weight-bolder text-grey-8 uppercase tracking-widest section-title">
            Signed up
          </div>
          <q-badge
            color="accent"
            :label="activeParticipants.length"
            rounded
            class="text-weight-bold count-badge"
          />
        </div>

        <div v-if="participantsLoading" class="row q-gutter-xs">
          <q-skeleton
            v-for="i in 5"
            :key="i"
            type="rect"
            :width="isMobile ? '48px' : '64px'"
            :height="isMobile ? '24px' : '28px'"
            class="rounded-borders"
          />
        </div>

        <template v-else-if="participantsLoaded">
          <div v-if="activeParticipants.length">
            <!-- Preliminary leagues notice -->
            <div
              v-if="projectedLeagueGroups.length"
              class="text-caption text-grey-6 italic q-mb-sm"
            >
              Provisional Leagues
            </div>

            <!-- Grouped by projected league -->
            <div class="league-grid" :class="{ 'league-grid--mobile': isMobile }">
              <div
                v-for="group in projectedLeagueGroups"
                :key="`L-${group.level}`"
                class="league-box"
              >
                <div class="league-box__label row items-center q-gutter-x-xs">
                  <LeagueLevel
                    badge
                    :level="group.level"
                    :style="isMobile ? 'font-size: 0.6rem' : 'font-size: 0.65rem'"
                  />
                  <q-badge
                    color="grey-5"
                    :label="`${group.members.length}/${group.size}`"
                    rounded
                    class="text-weight-bold"
                    style="font-size: 9px; padding: 1px 4px"
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
            </div>

            <!-- Newcomers -->
            <div v-if="newcomers.length" :class="isMobile ? 'q-mt-sm' : 'q-mt-md'">
              <div class="row items-center q-gutter-x-xs q-mb-xs">
                <div class="text-caption text-weight-bolder text-grey-7 uppercase tracking-widest section-title">
                  Newcomers
                </div>
                <q-badge
                  color="warning"
                  :label="newcomers.length"
                  rounded
                  class="text-weight-bold count-badge"
                />
                <q-icon name="person_add" size="12px" class="text-grey-6" />
              </div>
              <div class="row q-gutter-xs">
                <div v-for="(p, index) in newcomers" :key="p.profile || index" class="col-auto">
                  <div
                    class="participant-chip participant-chip--newcomer"
                    :class="{ 'participant-chip--mobile': isMobile }"
                  >
                    {{ p.profile_name || 'Anonymous' }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Fallback: signed-up users not yet in projection -->
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

          <!-- Missing Participants from previous season -->
          <div v-if="missingParticipants.length" :class="isMobile ? 'q-mt-md' : 'q-mt-lg'">
            <div class="row items-center q-gutter-x-xs q-mb-xs">
              <div class="text-caption text-weight-bolder text-grey-6 uppercase tracking-widest section-title">
                Missing from previous season
              </div>
              <q-badge
                color="grey-6"
                :label="missingParticipants.length"
                rounded
                class="text-weight-bold count-badge"
              />
            </div>
            <div class="row q-gutter-xs">
              <div v-for="(p, index) in missingParticipants" :key="p.id || index" class="col-auto">
                <div
                  class="participant-chip participant-chip--missing"
                  :class="{ 'participant-chip--mobile': isMobile }"
                >
                  <q-icon name="history" size="12px" class="q-mr-xs text-grey-5 flex-shrink-0" />
                  <span>{{ p.profile_name || 'Anonymous' }}</span>
                </div>
              </div>
            </div>
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
import LeagueLevel from 'components/season/LeagueLevel.vue';
import { useQuasar } from 'quasar';
import {
  fetchRegistrationStatus,
  fetchProjectedLeagues,
  registerForSeason,
} from 'src/services/seasonService';
import type {
  TProjectedLeague,
  TProjectedLeagueMember,
} from 'src/services/seasonService';
import type { TAnnouncementDto } from 'src/types';

const props = defineProps<{
  announcement: TAnnouncementDto & { season_id?: number };
}>();

const { announcement } = props;

const $q = useQuasar();
const { isMobile } = useResponsive();

const shouldRemoveBorders = computed(() => $q.screen.lt.sm);

const userStore = useUserStore();
const { isAuthenticated } = storeToRefs(userStore);

const isSignedUpForOpenSeason = ref(false);
const openSeasonId = ref<number | null>(null);
const participantsLoading = ref(false);
const participantsLoaded = ref(false);
const projectedLeagues = ref<TProjectedLeague[]>([]);
const newcomers = ref<TProjectedLeagueMember[]>([]);
const activeParticipants = ref<TProjectedLeagueMember[]>([]);
const missingParticipants = ref<TProjectedLeagueMember[]>([]);
const unprojectedParticipants = ref<TProjectedLeagueMember[]>([]);

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

const projectedLeagueGroups = computed<TProjectedLeague[]>(() => {
  return (projectedLeagues.value || []).filter((g) => g.members && g.members.length > 0);
});

async function loadParticipants() {
  if (participantsLoading.value) return;
  participantsLoading.value = true;
  try {
    const seasonId = announcement.season_id || openSeasonId.value || undefined;
    const proj = await fetchProjectedLeagues(seasonId);
    projectedLeagues.value = proj.leagues;
    newcomers.value = proj.newcomers;
    activeParticipants.value = proj.active_participants;
    missingParticipants.value = proj.missing_participants;
    unprojectedParticipants.value = proj.unprojected_participants;
  } catch {
    projectedLeagues.value = [];
    newcomers.value = [];
    activeParticipants.value = [];
    missingParticipants.value = [];
    unprojectedParticipants.value = [];
  } finally {
    participantsLoading.value = false;
    participantsLoaded.value = true;
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
  border-radius: 12px;
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.08);
  width: 100%;
}

.announcement-card--signup {
  border-top: 4px solid var(--q-accent);
  background: white;
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

.announcement-card:hover:not(.no-border-radius-mobile) {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  flex-shrink: 0;
  background: var(--q-accent);
}

.icon-wrapper--mobile {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  margin-right: 12px !important;
}

.lh-tight {
  line-height: 1.25;
}

.section-title {
  font-size: 0.65rem;
  letter-spacing: 0.08em;
}

.count-badge {
  font-size: 10px;
  padding: 1px 6px;
  line-height: 1.2;
}

.participant-chip {
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  line-height: 1.3;
  background: #f8fafc;
  padding: 4px 10px;
  border-radius: 6px;
  color: #1e293b;
  font-weight: 600;
  border: 1px solid rgba(94, 53, 177, 0.12);
  transition: all 0.15s ease-in-out;
}

.participant-chip:hover {
  background: #f1f5f9;
  border-color: rgba(94, 53, 177, 0.25);
}

.participant-chip--missing {
  background: #fcfcfc;
  color: #64748b;
  border: 1px dashed #cbd5e1;
  font-weight: 500;
  box-shadow: none;
}

.participant-chip--missing:hover {
  background: #f1f5f9;
  color: #475569;
}

.participant-chip--newcomer {
  background: #fffbeb;
  color: #b45309;
  border: 1px dashed #fcd34d;
  font-weight: 600;
  box-shadow: none;
}

.participant-chip--newcomer:hover {
  background: #fef3c7;
}

.participant-chip--mobile {
  font-size: 11px;
  padding: 2px 7px;
  border-radius: 5px;
}

.tracking-widest {
  letter-spacing: 0.08em;
}

.signup-minimized {
  cursor: pointer;
  transition: background-color 0.15s ease-in-out;
}

.signup-minimized:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.announcement-card--minimized {
  border-top-width: 4px;
  border-top-color: var(--q-accent) !important;
}

.league-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 8px;
}

.league-grid--mobile {
  grid-template-columns: 1fr;
  gap: 10px;
}

.league-box {
  position: relative;
  background: #fafafa;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  padding: 14px 10px 10px 10px;
  min-width: 0;
}

.league-box__label {
  position: absolute;
  top: -9px;
  left: 10px;
  background: white;
  border-radius: 4px;
  padding: 0 4px;
  line-height: 1;
}

.min-width-0 {
  min-width: 0;
}

.flex-shrink-0 {
  flex-shrink: 0;
}
</style>

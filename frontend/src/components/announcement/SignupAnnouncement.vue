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
        <div class="minimized-icon-badge flex flex-center q-mr-sm flex-shrink-0">
          <q-icon name="campaign" size="16px" color="white" />
        </div>
        <div class="text-subtitle2 text-weight-bolder announcement-title ellipsis">
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
          color="accent"
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
        <q-icon name="campaign" size="200px" color="accent" />
      </div>

      <!-- Top Row: Icon + Title & Actions -->
      <div class="row items-start no-wrap content-layer q-mb-md">
        <!-- Icon Circle -->
        <div
          class="icon-wrapper flex flex-center q-mr-md"
          :class="[isMobile ? 'icon-wrapper--mobile' : '']"
        >
          <q-icon
            name="campaign"
            :size="isMobile ? '26px' : '32px'"
            color="white"
          />
        </div>

        <!-- Title and Subtitle / Content -->
        <div class="col min-width-0 q-mr-sm">
          <div class="row items-center q-mb-xs">
            <span class="announcement-pill">
              <q-icon name="campaign" size="12px" class="q-mr-xs" />
              ANNOUNCEMENT
            </span>
          </div>
          <div class="text-h6 text-weight-bolder lh-tight announcement-title q-mb-xs">
            {{ announcement.title }}
          </div>
          <div
            v-if="announcement.content"
            class="text-subtitle2 announcement-desc"
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
            class="q-px-sm text-weight-bold signup-btn"
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
  background: var(--kenner-card-bg);
  border: 1px solid var(--kenner-border-color);
  width: 100%;
}

.announcement-card--signup {
  background:
    radial-gradient(circle at 100% 0%, rgba(94, 53, 177, 0.09) 0%, transparent 50%),
    radial-gradient(circle at 0% 100%, rgba(255, 122, 89, 0.06) 0%, transparent 40%),
    linear-gradient(135deg, #fbf7ff 0%, #f6f0fe 50%, #ffffff 100%);
  border: 1px solid rgba(94, 53, 177, 0.22);
  border-top: 4px solid var(--q-accent);
  box-shadow: 0 4px 20px rgba(94, 53, 177, 0.08), 0 1px 3px rgba(0, 0, 0, 0.03);
  position: relative;
}

.announcement-pill {
  display: inline-flex;
  align-items: center;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--q-accent);
  background: rgba(94, 53, 177, 0.1);
  border: 1px solid rgba(94, 53, 177, 0.2);
  padding: 1px 7px;
  border-radius: 10px;
  line-height: 1.4;
}

.announcement-title {
  color: #2e1065;
}

.announcement-desc {
  color: var(--kenner-text-secondary);
}

.signup-ornament {
  opacity: 0.06;
  pointer-events: none;
  transform: rotate(-12deg) translateY(5%);
  z-index: 0;
}

.content-layer {
  z-index: 1;
}

.announcement-card:hover:not(.no-border-radius-mobile) {
  box-shadow: 0 8px 25px rgba(94, 53, 177, 0.12), 0 2px 6px rgba(0, 0, 0, 0.04);
}

.icon-wrapper {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  flex-shrink: 0;
  background: linear-gradient(135deg, #7e57c2 0%, #5e35b1 100%);
  box-shadow: 0 4px 14px rgba(94, 53, 177, 0.35);
}

.icon-wrapper--mobile {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  margin-right: 12px !important;
}

.minimized-icon-badge {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: linear-gradient(135deg, #7e57c2 0%, #5e35b1 100%);
  box-shadow: 0 2px 6px rgba(94, 53, 177, 0.25);
}

.signup-btn {
  box-shadow: 0 3px 10px rgba(94, 53, 177, 0.3);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.signup-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(94, 53, 177, 0.4);
}

.lh-tight {
  line-height: 1.25;
}

.section-title {
  font-size: 0.65rem;
  letter-spacing: 0.08em;
  color: #581c87;
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
  background: var(--kenner-card-bg);
  padding: 4px 10px;
  border-radius: 6px;
  color: var(--kenner-text-color);
  font-weight: 600;
  border: 1px solid rgba(94, 53, 177, 0.16);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  transition: all 0.15s ease-in-out;
}

.participant-chip:hover {
  background: #f5f3ff;
  border-color: rgba(94, 53, 177, 0.35);
}

.participant-chip--missing {
  background: rgba(255, 255, 255, 0.75);
  color: var(--kenner-text-muted);
  border: 1px dashed #cbd5e1;
  font-weight: 500;
  box-shadow: none;
}

.participant-chip--missing:hover {
  background: var(--kenner-surface-muted);
  color: var(--kenner-text-secondary);
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
  background: linear-gradient(90deg, #faf5ff 0%, #ffffff 100%);
  transition: background-color 0.15s ease-in-out;
}

.signup-minimized:hover {
  background: linear-gradient(90deg, #f3e8ff 0%, #faf5ff 100%);
}

.announcement-card--minimized {
  border-top-width: 3px;
  border-top-color: var(--q-accent) !important;
  border-color: rgba(94, 53, 177, 0.2);
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
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(94, 53, 177, 0.16);
  border-radius: 8px;
  padding: 14px 10px 10px 10px;
  min-width: 0;
  box-shadow: 0 1px 4px rgba(94, 53, 177, 0.03);
}

.league-box__label {
  position: absolute;
  top: -9px;
  left: 10px;
  background: var(--kenner-card-bg);
  border: 1px solid rgba(94, 53, 177, 0.15);
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

/* Dark mode */
.body--dark .announcement-card--signup {
  background:
    radial-gradient(circle at 100% 0%, rgba(149, 117, 205, 0.16) 0%, transparent 50%),
    radial-gradient(circle at 0% 100%, rgba(255, 122, 89, 0.08) 0%, transparent 40%),
    linear-gradient(135deg, #221c2e 0%, #1e1a28 50%, #1a1a20 100%);
  border-color: rgba(149, 117, 205, 0.3);
  border-top-color: var(--q-accent);
}

.body--dark .announcement-pill {
  color: var(--kenner-accent-text);
  background: var(--kenner-accent-bg);
  border-color: rgba(149, 117, 205, 0.35);
}

.body--dark .announcement-title {
  color: #e9d5ff;
}

.body--dark .section-title {
  color: #d8b4fe;
}

.body--dark .participant-chip {
  border-color: rgba(149, 117, 205, 0.25);
}

.body--dark .participant-chip:hover {
  background: rgba(149, 117, 205, 0.18);
  border-color: rgba(149, 117, 205, 0.45);
}

.body--dark .participant-chip--missing {
  background: var(--kenner-hover-bg);
  border-color: var(--kenner-border-strong);
}

.body--dark .participant-chip--missing:hover {
  background: var(--kenner-surface-muted);
}

.body--dark .participant-chip--newcomer {
  background: var(--kenner-warning-bg);
  color: var(--kenner-warning-text);
  border-color: rgba(252, 211, 77, 0.4);
}

.body--dark .participant-chip--newcomer:hover {
  background: rgba(245, 158, 11, 0.25);
}

.body--dark .signup-minimized {
  background: linear-gradient(90deg, rgba(149, 117, 205, 0.14) 0%, transparent 100%);
}

.body--dark .signup-minimized:hover {
  background: linear-gradient(90deg, rgba(149, 117, 205, 0.22) 0%, rgba(149, 117, 205, 0.08) 100%);
}

.body--dark .announcement-card--minimized {
  border-color: rgba(149, 117, 205, 0.3);
}

.body--dark .league-box {
  background: var(--kenner-surface-overlay);
  border-color: rgba(149, 117, 205, 0.25);
}

.body--dark .league-box__label {
  border-color: rgba(149, 117, 205, 0.25);
}
</style>

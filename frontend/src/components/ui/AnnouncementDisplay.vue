<template>
  <div v-if="visibleAnnouncements.length" :class="isMobile ? 'q-mb-sm' : 'q-mb-md'">
    <transition-group
      appear
      enter-active-class="animated fadeIn"
      leave-active-class="animated fadeOut"
    >
      <div v-for="a in visibleAnnouncements" :key="a.id" class="q-mb-sm">
        <!-- TAnnouncementDto Card -->
        <q-card
          flat
          class="announcement-card overflow-hidden border-all"
          :class="[
            { 'no-border-radius': shouldRemoveBorders },
          ]"
        >
          <q-card-section
            :class="[
              isMobile ? 'q-py-sm' : 'q-py-md',
              'relative-position row items-start no-wrap'
            ]"
          >
            <!-- Colored accent bar -->
            <div
              class="absolute-left full-height accent-bar"
              :class="typeColors[a.type].split(' ')[0]"
            ></div>

            <!-- Content Header (Icon + Text) -->
            <div class="row items-start no-wrap col q-pl-sm">
              <!-- Icon Circle -->
              <div
                v-if="announcementIcons[a.type]"
                class="icon-wrapper flex flex-center q-mr-md"
                :class="[typeColors[a.type], isMobile ? 'icon-wrapper--mobile q-mt-xs' : '']"
              >
                <q-icon :name="announcementIcons[a.type]" :size="isMobile ? '16px' : '20px'" />
              </div>

              <!-- Content -->
              <div class="col" :class="!isMobile ? 'q-pr-xl' : 'q-pr-md'">
                <div
                  class="text-subtitle1 text-weight-bold lh-tight"
                  :class="textColors[a.type]"
                >
                  {{ a.title }}
                </div>
                <div v-if="a.content" class="text-body2 text-grey-8 q-mt-xs">
                  {{ a.content }}
                </div>

                <!-- Action Buttons (Mobile: below content, Desktop: right side) -->
                <div
                  v-if="isMobile && a.type === 'REGISTER'"
                  class="row items-center q-gutter-sm q-mt-sm"
                >
                  <KennerButton
                    flat
                    dense
                    no-caps
                    color="primary"
                    class="text-caption rounded-borders q-px-md border-all"
                    @click="toggleParticipants"
                  >
                    <q-icon :name="showParticipants ? 'expand_less' : 'people'" size="16px" class="q-mr-xs" />
                    {{ showParticipants ? 'Hide' : 'View' }} participants
                  </KennerButton>

                  <KennerButton
                    v-if="!isRegisteredForOpenSeason"
                    unelevated
                    dense
                    no-caps
                    color="primary"
                    :disable="!isAuthenticated"
                    class="q-px-md rounded-borders"
                    @click="register"
                  >
                    Register
                    <KennerTooltip v-if="!isAuthenticated" class="bg-grey-9">
                      Login to register for upcoming season
                    </KennerTooltip>
                  </KennerButton>

                  <div v-else class="row items-center q-gutter-x-xs text-positive text-weight-bold text-caption q-px-sm">
                    <q-icon name="check_circle" size="16px" />
                    <span>Registered</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Actions (Desktop all, Mobile only Close) -->
            <div
              class="row items-center q-gutter-sm absolute-right q-pa-sm"
              :class="isMobile ? 'q-ml-xs' : 'q-ml-sm'"
            >
              <template v-if="!isMobile && a.type === 'REGISTER'">
                <KennerButton
                  flat
                  dense
                  no-caps
                  color="primary"
                  class="text-caption rounded-borders q-px-md border-all"
                  @click="toggleParticipants"
                >
                  <q-icon :name="showParticipants ? 'expand_less' : 'people'" size="16px" class="q-mr-xs" />
                  {{ showParticipants ? 'Hide' : 'View' }} participants
                </KennerButton>

                <KennerButton
                  v-if="!isRegisteredForOpenSeason"
                  unelevated
                  dense
                  no-caps
                  color="primary"
                  :disable="!isAuthenticated"
                  class="q-px-md rounded-borders"
                  @click="register"
                >
                  Register
                  <KennerTooltip v-if="!isAuthenticated" class="bg-grey-9">
                    Login to register for upcoming season
                  </KennerTooltip>
                </KennerButton>

                <div v-else class="row items-center q-gutter-x-xs text-positive text-weight-bold text-caption q-px-sm">
                  <q-icon name="check_circle" size="16px" />
                  <span>Registered</span>
                </div>
              </template>

              <!-- Hide/Minimize Button -->
              <KennerButton
                flat
                round
                dense
                icon="close"
                size="sm"
                color="grey-6"
                @click="minimizeAnnouncement(a)"
              >
                <KennerTooltip>Minimize announcement</KennerTooltip>
              </KennerButton>
            </div>
          </q-card-section>

          <!-- Expanded Participants Panel -->
          <q-slide-transition>
            <div v-if="a.type === 'REGISTER' && showParticipants">
              <q-separator />
              <div class="bg-grey-1 q-pa-md">
                <div v-if="participantsLoading" class="flex flex-center q-py-sm">
                  <q-spinner-grid size="20px" color="primary" />
                </div>

                <template v-else-if="participantsLoaded">
                  <div v-if="participants.length" class="row q-gutter-xs">
                    <div
                      v-for="p in participants"
                      :key="p.id"
                      class="col-auto"
                    >
                      <div class="text-caption bg-white q-px-sm q-py-xs rounded-borders border-all">
                        {{ p.profile_name || 'Anonymous' }}
                      </div>
                    </div>
                  </div>
                  <div
                    v-else
                    class="text-caption text-grey-6 text-center q-py-sm italic"
                  >
                    No participants registered yet. Be the first!
                  </div>
                </template>
              </div>
            </div>
          </q-slide-transition>
        </q-card>
      </div>
    </transition-group>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { ref, computed } from 'vue';
import { useAnnouncementStore } from 'stores/announcementStore';
import { useUserStore } from 'stores/userStore';
import { useUiStore } from 'src/stores/uiStore';
import { useResponsive } from 'src/composables/responsive';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import { useQuasar } from 'quasar';
import {
  fetchIsRegisteredForSeason,
  fetchOpenSeasonParticipants,
  registerForSeason,
} from 'src/services/seasonService';

const $q = useQuasar();
const { isMobile } = useResponsive();

const shouldRemoveBorders = computed(() => {
  return $q.screen.lt.sm;
});

const store = useAnnouncementStore();
const uiStore = useUiStore();
const { announcements } = storeToRefs(store);
const { announcementIcons } = store;

const { isAuthenticated } = useUserStore();

const isRegisteredForOpenSeason = ref(false);
isRegisteredForOpenSeason.value = await fetchIsRegisteredForSeason();

const participants = ref<any[] | null>(null);
const participantsLoading = ref(false);
const participantsLoaded = ref(false);
const showParticipants = ref(false);
const hiddenAnnouncements = ref<Record<number, boolean>>({});

const visibleAnnouncements = computed(() => {
  return announcements.value.filter(a => !hiddenAnnouncements.value[a.id] && !uiStore.isMinimized(`announcement-${a.id}`));
});

function minimizeAnnouncement(a: any) {
  uiStore.minimize({
    id: `announcement-${a.id}`,
    title: a.title,
    icon: announcementIcons[a.type as keyof typeof announcementIcons] || 'announcement',
    color: 'primary',
    type: 'announcement'
  });
}

function dismissAnnouncement(id: number) {
  hiddenAnnouncements.value[id] = true;
}

async function loadParticipants() {
  if (participantsLoaded.value || participantsLoading.value) return;

  participantsLoading.value = true;
  try {
    participants.value = await fetchOpenSeasonParticipants();
  } catch {
    participants.value = [];
  } finally {
    participantsLoading.value = false;
    participantsLoaded.value = true;
  }
}

async function toggleParticipants() {
  if (!showParticipants.value) {
    await loadParticipants();
  }
  showParticipants.value = !showParticipants.value;
}

async function register() {
  const { status } = await registerForSeason();
  if (status === 200) {
    isRegisteredForOpenSeason.value = true;
    participantsLoaded.value = false;
    await loadParticipants();
  }
}


const textColors = {
  INFO: 'text-primary',
  WINNER: 'text-warning',
  REGISTER: 'text-secondary',
  WARNING: 'text-negative',
  NEUTRAL: 'text-grey-9',
};

const typeColors = {
  INFO: 'bg-primary text-white',
  WINNER: 'bg-warning text-white',
  REGISTER: 'bg-secondary text-white',
  WARNING: 'bg-negative text-white',
  NEUTRAL: 'bg-grey-4 text-grey-9',
};
</script>

<style scoped>
.announcement-card {
  border-radius: 8px;
  transition: all 0.2s ease-in-out;
  background-color: white;
}

.accent-bar {
  width: 6px;
  border-radius: 4px 0 0 4px;
}

.no-border-radius {
  border-radius: 0 !important;
}

.no-border-radius .accent-bar {
  border-radius: 0 !important;
}

.announcement-card:hover:not(.no-border-radius) {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.icon-wrapper {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  flex-shrink: 0;
}

.icon-wrapper--mobile {
  width: 28px;
  height: 28px;
  margin-right: 8px !important;
}

.lh-tight {
  line-height: 1.2;
}

.border-all {
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.min-height-0 {
  min-height: unset;
}
</style>

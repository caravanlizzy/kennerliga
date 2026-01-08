<template>
  <div v-if="isVisible" :class="isMobile ? 'q-mb-sm' : 'q-mb-md'">
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

                <!-- Integrated Participants List -->
                <div v-if="a.type === 'REGISTER'" class="q-mt-md">
                  <div class="row items-center q-gutter-x-sm q-mb-xs">
                    <div class="text-caption text-weight-bold text-grey-7 uppercase tracking-wider">
                      Participants
                    </div>
                    <q-badge color="secondary" :label="participants?.length ?? 0" rounded class="text-weight-bold" style="font-size: 10px; padding: 2px 6px;" />
                  </div>

                  <div v-if="participantsLoading" class="row q-gutter-xs">
                    <q-skeleton v-for="i in 5" :key="i" type="rect" width="60px" height="22px" class="rounded-borders" />
                  </div>
                  <template v-else-if="participantsLoaded">
                    <div v-if="participants?.length" class="row q-gutter-xs">
                      <div
                        v-for="p in participants"
                        :key="p.id"
                        class="col-auto"
                      >
                        <div class="participant-chip border-all">
                          {{ p.profile_name || 'Anonymous' }}
                        </div>
                      </div>
                    </div>
                    <div
                      v-else
                      class="text-caption text-grey-6 italic"
                    >
                      No participants yet.
                    </div>
                  </template>
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
const hiddenAnnouncements = ref<Record<number, boolean>>({});

const hasRegisterAnnouncement = computed(() => {
  return announcements.value.some(a => a.type === 'REGISTER');
});

const visibleAnnouncements = computed(() => {
  return announcements.value.filter(a => !hiddenAnnouncements.value[a.id]);
});

const isVisible = computed(() => {
  return visibleAnnouncements.value.length > 0;
});

import { watch } from 'vue';
watch(hasRegisterAnnouncement, (hasReg) => {
  if (hasReg) {
    loadParticipants();
  }
}, { immediate: true });

function minimizeAnnouncement(a: any) {
  hiddenAnnouncements.value[a.id] = true;
}

async function loadParticipants() {
  if (participantsLoading.value) return;

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

async function register() {
  const { status } = await registerForSeason();
  if (status === 200) {
    isRegisteredForOpenSeason.value = true;
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

.participant-chip {
  font-size: 11px;
  background: #f8f9fa;
  padding: 3px 8px;
  border-radius: 4px;
  color: #2c3e50;
  font-weight: 500;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.tracking-wider {
  letter-spacing: 0.05em;
}

.min-height-0 {
  min-height: unset;
}
</style>

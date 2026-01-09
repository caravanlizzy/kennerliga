<template>
  <div v-if="isVisible" :class="isMobile ? 'q-mb-sm' : 'q-mb-lg'">
    <transition-group
      appear
      enter-active-class="animated fadeInDown"
      leave-active-class="animated fadeOutUp"
    >
      <div v-for="a in visibleAnnouncements" :key="a.id" class="q-mb-md">
        <!-- TAnnouncementDto Card -->
        <q-card
          flat
          class="announcement-card overflow-hidden"
          :class="[
            { 'no-border-radius': shouldRemoveBorders },
            `announcement-card--${a.type.toLowerCase()}`
          ]"
        >
          <q-card-section
            :class="[
              isMobile ? 'q-py-md' : 'q-py-lg',
              'relative-position row items-center no-wrap'
            ]"
          >
            <!-- Content Header (Icon + Text) -->
            <div class="row items-center no-wrap col q-px-md">
              <!-- Icon Circle -->
              <div
                v-if="announcementIcons[a.type]"
                class="icon-wrapper flex flex-center q-mr-lg"
                :class="[typeColors[a.type], isMobile ? 'icon-wrapper--mobile' : '']"
              >
                <q-icon :name="announcementIcons[a.type]" :size="isMobile ? '20px' : '24px'" />
              </div>

              <!-- Content -->
              <div class="col">
                <div
                  class="text-h6 text-weight-bolder lh-tight"
                  :class="textColors[a.type]"
                >
                  {{ a.title }}
                </div>
                <div v-if="a.content" class="text-subtitle2 text-grey-8 q-mt-xs">
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
                <div v-if="a.type === 'REGISTER'" class="q-mt-lg">
                  <div class="row items-center q-gutter-x-sm q-mb-sm">
                    <div class="text-caption text-weight-bolder text-grey-8 uppercase tracking-widest" style="font-size: 0.65rem">
                      Registered Players
                    </div>
                    <q-badge color="secondary" :label="participants?.length ?? 0" rounded class="text-weight-bold" style="font-size: 10px; padding: 2px 6px;" />
                  </div>

                  <div v-if="participantsLoading" class="row q-gutter-xs">
                    <q-skeleton v-for="i in 5" :key="i" type="rect" width="60px" height="28px" class="rounded-borders" />
                  </div>
                  <template v-else-if="participantsLoaded">
                    <div v-if="participants?.length" class="row q-gutter-sm">
                      <div
                        v-for="p in participants"
                        :key="p.id"
                        class="col-auto"
                      >
                        <div class="participant-chip">
                          {{ p.profile_name || 'Anonymous' }}
                        </div>
                      </div>
                    </div>
                    <div
                      v-else
                      class="text-caption text-grey-6 italic"
                    >
                      No participants yet. Be the first to join!
                    </div>
                  </template>
                </div>
              </div>
            </div>

            <!-- Actions (Desktop all, Mobile only Close) -->
            <div
              class="row items-center q-gutter-sm absolute-top-right q-pa-md"
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
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.announcement-card--info { background: #e3f2fd; border-color: #bbdefb; }
.announcement-card--winner { background: #fff8e1; border-color: #ffecb3; }
.announcement-card--register { background: #e0f2f1; border-color: #b2dfdb; }
.announcement-card--warning { background: #ffebee; border-color: #ffcdd2; }
.announcement-card--neutral { background: #f5f5f5; border-color: #e0e0e0; }

.no-border-radius {
  border-radius: 0 !important;
}

.announcement-card:hover:not(.no-border-radius) {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  flex-shrink: 0;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.icon-wrapper--mobile {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  margin-right: 12px !important;
}

.lh-tight {
  line-height: 1.2;
}

.border-all {
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.participant-chip {
  font-size: 12px;
  background: white;
  padding: 4px 12px;
  border-radius: 8px;
  color: #2c3e50;
  font-weight: 600;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

.tracking-widest {
  letter-spacing: 0.1em;
}

.min-height-0 {
  min-height: unset;
}
</style>

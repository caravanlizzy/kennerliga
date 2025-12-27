<template>
  <div v-if="announcements.length" :class="isMobile ? 'q-mb-md' : 'q-mb-lg'">
    <div v-for="a in announcements" :key="a.id" class="q-mb-md">
      <!-- TAnnouncement Card -->
      <q-card
        flat
        bordered
        class="announcement-card overflow-hidden"
        :class="[
          cardThemes[a.type],
          { 'no-border-radius': shouldRemoveBorders },
        ]"
      >
        <q-card-section
          class="q-py-md"
          :class="isMobile ? 'column' : 'row items-center no-wrap'"
        >
          <!-- Content Header (Icon + Text) -->
          <div class="row items-center no-wrap col">
            <!-- Icon Circle -->
            <div
              v-if="announcementIcons[a.type]"
              class="icon-wrapper flex flex-center q-mr-md"
              :class="typeColors[a.type]"
            >
              <q-icon :name="announcementIcons[a.type]" size="18px" />
            </div>

            <!-- Content -->
            <div class="col">
              <div
                class="text-subtitle2 text-weight-bold lh-tight"
                :class="textColors[a.type]"
              >
                {{ a.title }}
              </div>
              <div v-if="a.content" class="text-caption text-grey-8 q-mt-xs">
                {{ a.content }}
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div
            v-if="a.type === 'REGISTER'"
            class="row items-center q-gutter-sm"
            :class="isMobile ? 'q-mt-md q-ml-none' : 'q-ml-sm'"
          >
            <q-btn
              flat
              dense
              no-caps
              color="primary"
              class="text-caption rounded-borders q-px-sm"
              @click="toggleParticipants"
            >
              {{ showParticipants ? 'Hide' : 'View' }} participants
            </q-btn>

            <KennerButton
              v-if="!isRegisteredForOpenSeason"
              unelevated
              dense
              color="primary"
              :disable="!isAuthenticated"
              class="q-px-md"
              @click="register"
            >
              Register
              <q-tooltip v-if="!isAuthenticated" class="bg-grey-9">
                Login to register for upcoming season
              </q-tooltip>
            </KennerButton>

            <q-chip
              v-else
              icon="check_circle"
              color="positive"
              text-color="white"
              dense
              outline
              size="sm"
            >
              Registered
            </q-chip>
          </div>
        </q-card-section>

        <!-- Expanded Participants Panel -->
        <q-slide-transition>
          <div v-if="a.type === 'REGISTER' && showParticipants">
            <q-separator />
            <div class="bg-grey-1 q-pa-md">
              <div v-if="participantsLoading" class="flex flex-center q-py-sm">
                <q-spinner size="20px" color="primary" />
              </div>

              <template v-else-if="participantsLoaded">
                <div v-if="participants.length" class="row q-col-gutter-xs">
                  <div
                    v-for="p in participants"
                    :key="p.id"
                    class="col-6 col-sm-4 text-caption text-grey-9"
                  >
                    <q-item dense class="q-pa-none min-height-0">
                      <q-item-section side class="q-pr-xs">
                        <q-icon name="person" size="12px" color="grey-5" />
                      </q-item-section>
                      <q-item-section>{{
                          p.profile_name || 'Anonymous'
                        }}</q-item-section>
                    </q-item>
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
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { ref, computed } from 'vue';
import { useAnnouncementStore } from 'stores/announcementStore';
import { useUserStore } from 'stores/userStore';
import { useResponsive } from 'src/composables/responsive';
import KennerButton from 'components/base/KennerButton.vue';
import { useQuasar } from 'quasar';
import {
  fetchIsRegisteredForSeason,
  fetchOpenSeasonParticipants,
  registerForSeason,
} from 'src/services/seasonService';

const $q = useQuasar();
const { isMobile } = useResponsive();

const shouldRemoveBorders = computed(() => {
  return isMobile || $q.screen.width < 1300;
});

const store = useAnnouncementStore();
const { announcements } = storeToRefs(store);
const { announcementIcons } = store;

const { isAuthenticated } = useUserStore();

const isRegisteredForOpenSeason = ref(false);
isRegisteredForOpenSeason.value = await fetchIsRegisteredForSeason();

const participants = ref<any[] | null>(null);
const participantsLoading = ref(false);
const participantsLoaded = ref(false);
const showParticipants = ref(false);

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

const cardThemes = {
  INFO: 'theme-info',
  WINNER: 'theme-winner',
  REGISTER: 'theme-register',
  WARNING: 'theme-warning',
  NEUTRAL: 'theme-neutral',
};

const textColors = {
  INFO: 'text-blue-10',
  WINNER: 'text-amber-10',
  REGISTER: 'text-deep-purple-10',
  WARNING: 'text-red-10',
  NEUTRAL: 'text-grey-9',
};

const typeColors = {
  INFO: 'bg-blue-2 text-blue-9',
  WINNER: 'bg-amber-2 text-amber-9',
  REGISTER: 'bg-deep-purple-2 text-deep-purple-9',
  WARNING: 'bg-red-2 text-red-9',
  NEUTRAL: 'bg-grey-3 text-grey-8',
};
</script>

<style scoped>
.announcement-card {
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  border-left-width: 6px !important;
}

.no-border-radius {
  border-radius: 0 !important;
  border-left-width: 0 !important;
  border-right-width: 0 !important;
  border-top-width: 0 !important;
}

.announcement-card:hover:not(.no-border-radius) {
  border-color: #bdbdbd;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* Theme Accents */
.theme-info {
  border-left-color: var(--q-primary) !important;
  background-color: #f0f7ff;
}
.theme-winner {
  border-left-color: var(--q-warning) !important;
  background-color: #fffbef;
}
.theme-register {
  border-left-color: var(--q-secondary) !important;
  background-color: #f7f2ff;
}
.theme-warning {
  border-left-color: var(--q-negative) !important;
  background-color: #fff5f5;
}
.theme-neutral {
  border-left-color: var(--q-grey-6) !important;
  background-color: #fafafa;
}

.icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  flex-shrink: 0;
}

.lh-tight {
  line-height: 1.2;
}

.min-height-0 {
  min-height: unset;
}
</style>

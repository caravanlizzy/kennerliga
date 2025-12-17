<template>
  <div v-if="announcements.length">
    <div class="row justify-center">
      <div class="col-12">
        <div v-for="a in announcements" :key="a.id" class="q-mb-sm">
          <q-banner
            dense
            rounded
            class="q-px-md q-py-sm border-left"
            :class="backgroundColors[a.type]"
          >
            <div class="row items-center no-wrap">
              <!-- Icon -->
              <div class="q-pa-xs q-mr-sm flex flex-center rounded-borders">
                <q-icon
                  :name="announcementIcons[a.type]"
                  size="16px"
                  class="text-white"
                />
              </div>

              <!-- Text -->
              <div class="col">
                <div class="text-body2 text-white text-weight-medium">
                  {{ a.title }}
                </div>

                <div v-if="a.content" class="text-caption q-mt-xs text-white">
                  {{ a.content }}
                </div>

                <!-- Participants section INSIDE the banner -->
                <q-slide-transition v-if="a.type === 'REGISTER'">
                  <div v-show="showParticipants" class="q-mt-sm">
                    <q-separator dark class="q-mb-xs" />

                    <div class="row items-center justify-between q-mb-xs">
                      <q-spinner
                        v-if="participantsLoading"
                        size="16px"
                        color="white"
                      />
                    </div>

                    <div v-if="participantsLoaded && participants.length">
                      <q-list dense class="bg-transparent">
                        <div class="row">
                          <div
                            class="col-6"
                            v-for="p in participants"
                            :key="p.id"
                          >
                            <span class="text-caption text-white">
                              {{ p.profile_name || 'Unknown' }}
                            </span>
                          </div>
                        </div>
                      </q-list>
                    </div>

                    <div
                      v-else-if="participantsLoaded && !participants.length"
                      class="text-caption text-grey-4"
                    >
                      No participants registered yet. Be the first!
                    </div>
                  </div>
                </q-slide-transition>
              </div>
            </div>

            <template #action>
              <div class="row items-center q-gutter-sm">
                <!-- Toggle participants list -->
                <KennerButton
                  v-if="a.type === 'REGISTER'"
                  flat
                  color="warning"
                  class="text-caption"
                  @click="toggleParticipants"
                >
                  {{ showParticipants ? 'Hide Players' : 'Show Players' }}
                </KennerButton>
                <KennerButton
                  v-if="a.type === 'REGISTER' && !isRegisteredForOpenSeason"
                  flat
                  color="white"
                  :disable="!isAuthenticated"
                  @click="register"
                >
                  Register
                  <q-tooltip v-if="!isAuthenticated">
                    Login to register for upcoming season
                  </q-tooltip>
                </KennerButton>
              </div>
            </template>
          </q-banner>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useAnnouncementStore } from 'stores/announcementStore';
import KennerButton from 'components/base/KennerButton.vue';
import { useUserStore } from 'stores/userStore';
import {
  fetchIsRegisteredForSeason,
  fetchOpenSeasonParticipants,
  registerForSeason,
} from 'src/services/seasonService';
import { ref } from 'vue';

const store = useAnnouncementStore();
const { isAuthenticated } = useUserStore();
const { announcements } = storeToRefs(store);
const { announcementIcons } = store;

const isRegisteredForOpenSeason = ref(false);
isRegisteredForOpenSeason.value = await fetchIsRegisteredForSeason();

// participants for current open season
const participants = ref<any[]>([]);
const participantsLoading = ref(false);
const participantsLoaded = ref(false);
const showParticipants = ref(false);

async function loadParticipants() {
  if (participantsLoaded.value || participantsLoading.value) return;

  participantsLoading.value = true;
  try {
    participants.value = await fetchOpenSeasonParticipants();
  } catch (err) {
    console.error('Failed to load participants', err);
    participants.value = [];
  } finally {
    participantsLoading.value = false;
    participantsLoaded.value = true;
  }
}

async function toggleParticipants() {
  if (!showParticipants.value) {
    // opening
    await loadParticipants();
    showParticipants.value = true;
  } else {
    // closing
    showParticipants.value = false;
  }
}

async function register() {
  const { status } = await registerForSeason();
  if (status === 200) {
    isRegisteredForOpenSeason.value = true;
    // optionally refresh participants when user registers
    participantsLoaded.value = false;
    await loadParticipants();
  }
}

const backgroundColors = {
  INFO: 'bg-blue-grey-8',
  WINNER: 'bg-secondary',
  REGISTER: 'bg-accent',
  WARNING: 'bg-negative',
  NEUTRAL: 'bg-grey-7',
};
</script>

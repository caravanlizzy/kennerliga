<template>
  <q-card
    flat
    class="announcement-card overflow-hidden announcement-card--register"
    :class="{ 'no-border-radius': shouldRemoveBorders }"
  >
    <q-card-section
      :class="[
        isMobile ? 'q-py-md' : 'q-py-lg',
        'relative-position row items-center no-wrap',
      ]"
    >
      <!-- Content Header (Icon + Text) -->
      <div class="row items-center no-wrap col q-px-md">
        <!-- Icon Circle -->
        <div
          class="icon-wrapper flex flex-center q-mr-lg bg-secondary text-white"
          :class="[isMobile ? 'icon-wrapper--mobile' : '']"
        >
          <q-icon name="how_to_reg" :size="isMobile ? '20px' : '24px'" />
        </div>

        <!-- Content -->
        <div class="col">
          <div class="text-h6 text-weight-bolder lh-tight text-secondary">
            {{ announcement.title }}
          </div>
          <div
            v-if="announcement.content"
            class="text-subtitle2 text-grey-8 q-mt-xs"
          >
            {{ announcement.content }}
          </div>

          <!-- Action Buttons (Mobile: below content, Desktop: right side) -->
          <div v-if="isMobile" class="row items-center q-gutter-sm q-mt-sm">
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

            <div
              v-else
              class="row items-center q-gutter-x-xs text-positive text-weight-bold text-caption q-px-sm"
            >
              <q-icon name="check_circle" size="16px" />
              <span>Registered</span>
            </div>
          </div>

          <!-- Integrated Participants List -->
          <div class="q-mt-lg">
            <div class="row items-center q-gutter-x-sm q-mb-sm">
              <div
                class="text-caption text-weight-bolder text-grey-8 uppercase tracking-widest"
                style="font-size: 0.65rem"
              >
                Registered Players
              </div>
              <q-badge
                color="secondary"
                :label="participants?.length ?? 0"
                rounded
                class="text-weight-bold"
                style="font-size: 10px; padding: 2px 6px"
              />
            </div>

            <div v-if="participantsLoading" class="row q-gutter-xs">
              <q-skeleton
                v-for="i in 5"
                :key="i"
                type="rect"
                width="60px"
                height="28px"
                class="rounded-borders"
              />
            </div>
            <template v-else-if="participantsLoaded">
              <div v-if="participants?.length" class="row q-gutter-sm">
                <div v-for="p in participants" :key="p.id" class="col-auto">
                  <div class="participant-chip">
                    {{ p.profile_name || 'Anonymous' }}
                  </div>
                </div>
              </div>
              <div v-else class="text-caption text-grey-6 italic">
                No participants yet. Be the first to join!
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- Actions (Desktop all) -->
      <div class="row items-center q-gutter-sm absolute-top-right q-pa-md">
        <template v-if="!isMobile">
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

          <div
            v-else
            class="row items-center q-gutter-x-xs text-positive text-weight-bold text-caption q-px-sm"
          >
            <q-icon name="check_circle" size="16px" />
            <span>Registered</span>
          </div>
        </template>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { ref, onMounted } from 'vue';
import { useUserStore } from 'stores/userStore';
import { useResponsive } from 'src/composables/responsive';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import { useQuasar } from 'quasar';
import {
  fetchIsRegisteredForSeason,
  fetchOpenSeasonParticipants,
  fetchSeasonParticipants,
  registerForSeason,
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

const isRegisteredForOpenSeason = ref(false);
const participants = ref<TSeasonParticipantDto[] | null>(null);
const participantsLoading = ref(false);
const participantsLoaded = ref(false);

async function loadParticipants() {
  if (participantsLoading.value) return;
  participantsLoading.value = true;
  try {
    const seasonId = announcement.season_id;
    if (seasonId) {
      participants.value = await fetchSeasonParticipants(seasonId);
    } else {
      participants.value = await fetchOpenSeasonParticipants();
    }
  } catch {
    participants.value = [];
  } finally {
    participantsLoading.value = false;
    participantsLoaded.value = true;
  }
}

async function register() {
  const seasonId = announcement.season_id;
  if (!seasonId) {
    console.error('No season_id found in announcement');
    return;
  }
  const res = await registerForSeason(seasonId);
  if (res && res.status === 200) {
    isRegisteredForOpenSeason.value = true;
    await loadParticipants();
  }
}

onMounted(async () => {
  if (isAuthenticated.value) {
    isRegisteredForOpenSeason.value = await fetchIsRegisteredForSeason(
      announcement.season_id
    );
  }
  await loadParticipants();
});
</script>

<style scoped>
.announcement-card {
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.announcement-card--register {
  background: #e0f2f1;
  border-color: #b2dfdb;
}

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
</style>

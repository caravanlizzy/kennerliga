<template>
  <div v-if="isVisible" :class="isMobile ? 'q-mb-sm' : 'q-mt-md q-mb-lg'">
    <transition-group
      appear
      enter-active-class="animated fadeInDown"
      leave-active-class="animated fadeOutUp"
    >
      <div v-for="a in visibleAnnouncements" :key="a.id" class="q-mb-md">
        <!-- Special Handling for Registration -->
        <RegistrationAnnouncement
          v-if="a.type === 'REGISTER'"
          :announcement="a"
        />

        <!-- General TAnnouncementDto Card -->
        <q-card
          v-else
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
                :class="[isMobile ? 'icon-wrapper--mobile' : '']"
                :style="{ background: 'transparent', boxShadow: 'none' }"
              >
                <q-icon
                  :name="announcementIcons[a.type]"
                  :size="isMobile ? '28px' : '32px'"
                  :class="textColors[a.type]"
                />
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
              </div>
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
import { useResponsive } from 'src/composables/responsive';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import RegistrationAnnouncement from 'components/announcement/RegistrationAnnouncement.vue';
import { useQuasar } from 'quasar';

const $q = useQuasar();
const { isMobile } = useResponsive();

const shouldRemoveBorders = computed(() => {
  return $q.screen.lt.sm;
});

const store = useAnnouncementStore();
const { announcements } = storeToRefs(store);
const { announcementIcons } = store;

const visibleAnnouncements = computed(() => {
  return announcements.value;
});

const isVisible = computed(() => {
  return visibleAnnouncements.value.length > 0;
});

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
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-left-width: 6px;
  width: 100%;
}

.announcement-card--info {
  border-left-color: var(--q-primary) !important;
  background: linear-gradient(to right, rgba(55, 71, 79, 0.05), transparent);
}
.announcement-card--winner {
  border-left-color: var(--q-warning) !important;
  background: linear-gradient(to right, rgba(230, 126, 34, 0.05), transparent);
}
.announcement-card--register {
  border-left-color: var(--q-primary) !important;
  background: linear-gradient(to right, rgba(55, 71, 79, 0.05), transparent);
}
.announcement-card--warning {
  border-left-color: var(--q-negative) !important;
  background: linear-gradient(to right, rgba(214, 58, 56, 0.05), transparent);
}
.announcement-card--neutral {
  border-left-color: #9e9e9e !important;
  background: linear-gradient(to right, rgba(158, 158, 158, 0.05), transparent);
}

.no-border-radius {
  border-radius: 0 !important;
}

.announcement-card:hover:not(.no-border-radius) {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  background: rgba(255, 255, 255, 0.8);
}

.icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 25% / 35%;
  flex-shrink: 0;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.icon-wrapper--mobile {
  width: 40px;
  height: 40px;
  border-radius: 25% / 35%;
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
  background: rgba(248, 249, 250, 0.7);
  padding: 4px 12px;
  border-radius: 8px;
  color: #2c3e50;
  font-weight: 600;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.tracking-widest {
  letter-spacing: 0.1em;
}

.min-height-0 {
  min-height: unset;
}
</style>

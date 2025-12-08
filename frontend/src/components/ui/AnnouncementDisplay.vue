<template>
  <div v-if="announcements.length" >
    <div class="row justify-center">
      <!-- centered, not full width -->
      <div class="col-12">
        <div
          v-for="a in announcements"
          :key="a.id"
          class="q-mb-sm"
        >
          <q-banner
            dense
            rounded
            class="q-px-md q-py-sm bg-white border-left"
            :style="{
              borderWidth: '1px',
              borderStyle: 'solid',
              borderColor: borderColors[a.type],
              borderLeftWidth: '3px',
            }"
          >
            <div class="row items-center no-wrap">
              <!-- Icon with subtle colored background -->
              <div
                class="q-pa-xs q-mr-sm flex flex-center rounded-borders"
                :class="iconBgClasses[a.type]"
              >
                <q-icon
                  :name="announcementIcons[a.type]"
                  size="16px"
                  :class="textColors[a.type]"
                />
              </div>

              <!-- Text -->
              <div class="col">
                <div class="text-body2 text-weight-medium">
                  {{ a.title }}
                </div>

                <div
                  v-if="a.content"
                  class="text-caption q-mt-xs text-grey-7"
                >
                  {{ a.content }}
                </div>
              </div>

              <!-- Right action slot (optional) -->
              <div v-if="$slots.actions" class="q-ml-sm">
                <slot name="actions" :announcement="a" />
              </div>
            </div>
          </q-banner>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useAnnouncementStore } from 'stores/announcementStore';
// if you have the type available, you can import it:
// import type { AnnouncementType } from 'src/models/announcementModel';

const store = useAnnouncementStore();
const { announcements } = storeToRefs(store);
const { announcementIcons } = store;

// keys assume a.type is one of: 'INFO' | 'WINNER' | 'REGISTER' | 'WARNING' | 'NEUTRAL'
// adjust if your enum/string values differ
const borderColors: Record<string, string> = {
  INFO: 'var(--q-info)',
  WINNER: 'var(--q-secondary)',
  REGISTER: 'var(--q-positive)',
  WARNING: 'var(--q-negative)',
  NEUTRAL: 'var(--q-grey-5)',
};

const textColors: Record<string, string> = {
  INFO: 'text-info',
  WINNER: 'text-secondary',
  REGISTER: 'text-positive',
  WARNING: 'text-negative',
  NEUTRAL: 'text-grey-7',
};

// subtle pastel background just for the icon circle
const iconBgClasses: Record<string, string> = {
  INFO: 'bg-info-1',
  WINNER: 'bg-secondary-1',
  REGISTER: 'bg-positive-1',
  WARNING: 'bg-negative-1',
  NEUTRAL: 'bg-grey-3',
};
</script>


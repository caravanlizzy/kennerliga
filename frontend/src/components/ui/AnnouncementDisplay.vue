<template>
  <div v-if="announcements.length" >
    <div class="row justify-center">
      <div class="col-12">
        <div
          v-for="a in announcements"
          :key="a.id"
          class="q-mb-sm"
        >
          <q-banner
            dense
            rounded
            class="q-px-md q-py-sm border-left"
            :class="backgroundColors[a.type]"
          >
            <div class="row items-center no-wrap">
              <!-- Icon with subtle colored background -->
              <div
                class="q-pa-xs q-mr-sm flex flex-center rounded-borders"
              >
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

                <div
                  v-if="a.content"
                  class="text-caption q-mt-xs text-white"
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

const backgroundColors = {
  INFO: 'bg-info',
  WINNER: 'bg-secondary',
  REGISTER: 'bg-positive',
  WARNING: 'bg-negative',
  NEUTRAL: 'bg-grey-7',
}
</script>


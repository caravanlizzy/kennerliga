<template>
  <div>
    <q-banner
      v-for="announcement in announcements"
      :key="announcement.id"
      :class="[bannerClasses[announcement.type], 'q-py-md']"
    >
      <!-- Center the content container -->
      <div class="full-width flex flex-center">
        <div
          class="column"
          style="max-width: 880px; width: 100%;"
        >
          <!-- Icon next to title, but text left-aligned -->
          <div class="row items-center q-gutter-sm">
            <q-icon
              :name="announcementIcons[announcement.type]"
              size="md"
            />

            <div class="text-subtitle1 text-weight-bold">
              {{ announcement.title }}
            </div>
          </div>

          <!-- Body text (left aligned) -->
          <div
            v-if="announcement.content"
            class="q-mt-sm text-body1"
          >
            {{ announcement.content }}
          </div>
        </div>
      </div>
    </q-banner>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useAnnouncementStore } from 'stores/announcementStore';

const announcementStore = useAnnouncementStore();
const { announcements } = storeToRefs(announcementStore);
const { bannerClasses, announcementIcons } = announcementStore;
</script>

<template>
  <div>
    <q-banner
      v-for="announcement in announcements"
      :key="announcement.id"
      :class="[bannerClasses[announcement.type], 'q-py-md']"
    >
      <div class="full-width flex flex-center">
        <div
          class="column items-center text-center"
          style="max-width:780px;"
        >
          <!-- Avatar + title row -->
          <div class="row items-center justify-center q-gutter-sm">
            <q-icon
              :name="announcementIcons[announcement.type]"
              size="md"
            />

            <div class="text-subtitle1 text-weight-bold">
              {{ announcement.title }}
            </div>
          </div>

          <!-- Optional content -->
          <div v-if="announcement.content" class="q-mt-sm">
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

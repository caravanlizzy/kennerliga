<template>
  <div>
    <q-banner
      v-for="announcement in announcements"
      :key="announcement.id"
      :class="bannerClasses[announcement.type]"
    >
      <template #avatar>
        <q-icon
          :name="announcementIcons[announcement.type]"
          size="md"
        />
      </template>

      <div class="text-subtitle1 text-weight-bold">
        {{ announcement.title }}
      </div>

      <div v-if="announcement.content" class="q-mt-xs">
        {{ announcement.content }}
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

<template>
  <div class="bg-white q-pa-md flex-center column">
    <AnnouncementCard
      :type="type"
      v-for="{ title, content, type } of announcements"
      :key="title + content"
    >
      <template v-if="title" #title> {{ title }}</template>
      <template v-if="content" #content> {{ content }}</template>
    </AnnouncementCard>
  </div>
</template>
<script setup lang="ts">
import AnnouncementCard from 'components/announcement/AnnouncementCard.vue';
import { useAnnouncementStore } from 'stores/announcementStore';

const { announcements, fetchAnnouncements } = useAnnouncementStore();
fetchAnnouncements();
</script>

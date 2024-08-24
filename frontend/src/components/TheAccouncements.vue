<template>
  <AnnouncementCard :type="type" v-for="{ title, content, type } of announcements" :key="title+content">
    <template v-if="title" #title> {{ title }}</template>
    <template v-if="content" #content> {{ content }}</template>
  </AnnouncementCard>
</template>
<script setup lang="ts">
import AnnouncementCard from "components/cards/AnnouncementCard.vue";
import { useAnnouncementStore } from "stores/announcementStore";
import { storeToRefs } from "pinia";
import { registerForCurrentSeason } from "src/services/season/seasonService";
import KennerButton from "components/buttons/KennerButton.vue";

const announcementStore = useAnnouncementStore();
const { announcements } = storeToRefs(announcementStore);
const { getAnnouncements } = announcementStore;
getAnnouncements();

</script>

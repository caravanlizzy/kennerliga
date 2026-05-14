<template>
  <div v-if="!isMobile" class="row">
    <AnnouncementDisplay class="col-12 q-px-md" />
  </div>

  <div v-else class="q-mb-md">
    <AnnouncementDisplay />
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'HomeAnnouncements' });
import AnnouncementDisplay from 'components/ui/AnnouncementDisplay.vue';

defineProps<{
  isMobile: boolean;
}>();
</script>

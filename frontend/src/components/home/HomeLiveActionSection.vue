<template>
  <ContentSection
    id="live-action"
    title="Live Action"
    icon="bolt"
    color="accent"
    class="col-12"
  >
    <LiveActionFeed />
  </ContentSection>
</template>

<script setup lang="ts">
defineOptions({ name: 'HomeLiveActionSection' });
import ContentSection from 'components/base/ContentSection.vue';
import LiveActionFeed from 'components/ui/LiveActionFeed.vue';
</script>

<template>
  <ContentSection
    id="live-action"
    title="Live Action"
    icon="bolt"
    color="info"
    class="col-12"
    no-margin
  >
    <template #header-extra>
      <KennerButton
        flat
        dense
        size="sm"
        color="info"
        icon="open_in_new"
        label="All"
        :to="{ name: 'live' }"
      />
    </template>
    <LiveActionFeed :max-items="5" />
  </ContentSection>
</template>

<script setup lang="ts">
defineOptions({ name: 'HomeLiveActionSection' });
import ContentSection from 'components/base/ContentSection.vue';
import LiveActionFeed from 'components/ui/LiveActionFeed.vue';
import KennerButton from 'components/base/KennerButton.vue';
</script>

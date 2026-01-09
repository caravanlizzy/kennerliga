<template>
  <q-page class="q-pa-md bg-white">
    <ContentSection
      id="live-action-mobile"
      title="Live Action"
      icon="bolt"
      color="accent"
      :bordered="false"
    >
      <LiveActionFeed />
    </ContentSection>
  </q-page>
</template>

<script setup lang="ts">
import LiveActionFeed from 'components/ui/LiveActionFeed.vue';
import ContentSection from 'components/base/ContentSection.vue';
import { onMounted } from 'vue';
import { useUiStore } from 'stores/uiStore';

const uiStore = useUiStore();
</script>

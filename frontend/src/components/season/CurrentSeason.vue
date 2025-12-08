<template>
  <SideAccentBox color="info" :class="isMobile ? '' : 'q-pa-md'">
    <SeasonScoreboards v-if="seasonId" :season-id="seasonId" />
    {{isMobile}}
  </SideAccentBox>
</template>

<script setup lang="ts">
import SideAccentBox from 'components/base/SideAccentBox.vue';
import SeasonScoreboards from 'components/season/SeasonScoreboards.vue';
import { useResponsive } from 'src/composables/reponsive';

defineProps<{ seasonId: number }>();

const { isMobile } = useResponsive();
</script>

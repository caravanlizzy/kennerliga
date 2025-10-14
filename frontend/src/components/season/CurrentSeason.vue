<template>
    <SideAccentBox color="info" class="current-season q-pa-md">
        <SeasonScoreboards v-if="seasonId" :season-id="seasonId" />
    </SideAccentBox>
</template>

<script setup lang="ts">

import SideAccentBox from 'components/base/SideAccentBox.vue';
import SeasonScoreboards from 'components/season/SeasonScoreboards.vue';

defineProps<{ seasonId: number }>();
</script>

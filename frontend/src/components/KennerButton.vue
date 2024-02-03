<template>
  <q-btn outline :dense="isMobile" :class="{ 'q-mx-xs' : isMobile }" :color="color" :to="{ name:forwardName}"
         :icon="icon"
         :label="label">
    <slot></slot>
  </q-btn>
</template>

<script setup lang="ts">

import { useResponsive } from 'src/composables/reponsive';
import { TKennerButton } from 'components/models';
defineProps<TKennerButton>();
const { isMobile } = useResponsive();

</script>

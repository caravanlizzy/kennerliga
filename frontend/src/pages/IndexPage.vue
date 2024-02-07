<template>
  <q-page class="q-pa-xl">
    <q-card dark flat :class="{'q-pa-xl': !isMobile}">
      <q-card-section class="text-h4 text-secondary">
        Willkommen zur Kennerliga...
      </q-card-section>

      <q-separator class="q-mb-lg" color="secondary" />

      <q-card-section class="text-h6">
        ...wo Ginooo unser großer Chief ist und Judith derzeit unschlagbar! Es sei denn, du mischst dich ein. Hier treffen
        die besten Zockerhirne aufeinander. Na, angefixt? Melde dich doch hier an:
      </q-card-section>

      <q-card-section>
        <q-icon name="pets" size="xl" color=secondary></q-icon>
      </q-card-section>

    </q-card>
  </q-page>
</template>

<script setup lang="ts">

import { useResponsive } from 'src/composables/reponsive';

const { isMobile } = useResponsive();

</script>

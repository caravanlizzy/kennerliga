

<template>
  <q-toggle label="Assymmentrisch"  :model-value="isAssymmetric" @update:model-value="isAssymmetric = !isAssymmetric"/>
  <q-toggle label="Startspielerreihenfolge"  :model-value="startingPlayerOrder" @update:model-value="startingPlayerOrder = !startingPlayerOrder"/>
  <q-toggle label="Punkte"  :model-value="hasPoints" @update:model-value="hasPoints = !hasPoints"/>

</template>

<script setup lang="ts">

import { ref } from 'vue';

const isAssymmetric = ref(false);
const startingPlayerOrder = ref(true);
const hasPoints = ref(true);

</script>

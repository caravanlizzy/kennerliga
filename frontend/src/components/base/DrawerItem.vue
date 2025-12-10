<template>
  <q-item :to="{name: forwardName}" @click="closeDrawer" clickable>
    <q-item-section>
      <KennerButton  color="dark" flat :icon="icon" />
    </q-item-section>
    <q-item-section >
      <q-item-label class="text-dark" caption> {{label}} </q-item-label>
    </q-item-section>
  </q-item>
</template>

<script setup lang="ts">
import KennerButton from 'components/base/KennerButton.vue';
import { inject } from 'vue';

type TKennerItem = {
  icon: string;
  iconColor?: string;
  label: string;
  forwardName?: string;
}
defineProps<TKennerItem>();

const closeDrawer = inject('closeDrawer');
</script>

<template>
  <q-item :to="{name: forwardName}" clickable>
    <q-item-section>
      <kenner-button  color="primary" flat :icon="icon" />
    </q-item-section>
    <q-item-section >
      <q-item-label class="text-primary" caption> {{label}} </q-item-label>
    </q-item-section>
  </q-item>
</template>

<script setup lang="ts">
import KennerButton from 'components/buttons/KennerButton.vue';

type TKennerItem = {
  icon: string;
  iconColor?: string;
  label: string;
  forwardName?: string;
}
defineProps<TKennerItem>();
</script>

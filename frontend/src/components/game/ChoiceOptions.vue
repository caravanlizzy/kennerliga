<template>
  <div v-for="option in options" :key="option.id">
    <OverviewCard v-bind="$attrs" v-if="option.has_choices">
      <template #title>
        {{ option.name }}
      </template>
      <template #content>
        <div class="text-bold">Auswahl</div>
        <q-separator />
        <ul v-for="choice of option.choices" :key="JSON.stringify(choice)">
          <li>{{ choice.name }}</li>
        </ul>
      </template>
    </OverviewCard>
  </div>
</template>
<script setup lang="ts">
import OverviewCard from 'components/cards/OverviewCard.vue';
import { TGameOptionDto } from 'src/types';

defineProps<{
  options: TGameOptionDto[];
}>();

defineOptions({
  inheritAttrs: false
});
</script>

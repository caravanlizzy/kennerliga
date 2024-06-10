<template>
  <div v-for="option in options" :key="option.id">
    <overview-card v-bind="$attrs" v-if="option.has_choices">
      <template #cardHeader>

        {{ option.name }}
      </template>
      <template #cardBody>
        <div class="text-bold">Auswahl</div>
        <q-separator />
        <ul v-for="choice of option.choices" :key="JSON.stringify(choice)">
          <li>{{ choice.name }}</li>
        </ul>
      </template>
    </overview-card>
  </div>
</template>
<script setup lang="ts">
import OverviewCard from 'components/cards/OverviewCard.vue';
import { GameOptionDto } from 'pages/game/models';

defineProps<{
  options: GameOptionDto[];
}>();

defineOptions({
  inheritAttrs: false
});
</script>

<template>
  <OverviewCard v-if="options.length" title="Toggle Options" icon="toggle_on" icon-color="primary">
    <template #header-extra>
      <q-badge color="secondary" class="q-px-sm" rounded>
        {{ options.length }} toggles
      </q-badge>
    </template>
    <template #content>
      <div class="row q-col-gutter-sm">
        <div v-for="option of options" :key="option.id" class="col-12 col-sm-6 col-md-4">
          <div class="row items-center q-pa-sm rounded-borders bg-grey-1 border-subtle q-gutter-x-sm">
            <q-icon name="check_circle" color="positive" size="18px" />
            <span class="text-body2 text-weight-medium text-dark ellipsis">{{ option.name }}</span>
          </div>
        </div>
      </div>
    </template>
  </OverviewCard>
</template>

<script setup lang="ts">
import OverviewCard from 'components/cards/OverviewCard.vue';
import { TGameOptionDto } from 'src/types';

defineProps<{
  options: TGameOptionDto[];
}>();
</script>

<style scoped lang="scss">
.border-subtle {
  border: 1px solid rgba(0, 0, 0, 0.05);
}
</style>

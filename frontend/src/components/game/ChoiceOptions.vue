<template>
  <div class="column q-gutter-y-md">
    <template v-for="option in options" :key="option.id">
      <OverviewCard v-if="option.has_choices" icon="list" icon-color="primary" v-bind="$attrs">
        <template #title>
          {{ option.name }}
        </template>
        <template #header-extra>
          <q-badge color="primary" class="q-px-sm" rounded>
            {{ option.choices?.length ?? 0 }} options
          </q-badge>
        </template>
        <template #content>
          <div class="row q-col-gutter-sm">
            <div
              v-for="choice of option.choices"
              :key="JSON.stringify(choice)"
              class="col-12 col-sm-6"
            >
              <div class="row items-center q-pa-sm rounded-borders bg-grey-1 border-subtle q-gutter-x-sm">
                <q-icon name="radio_button_checked" color="primary" size="16px" />
                <span class="text-body2 text-weight-medium text-dark">{{ choice.name }}</span>
              </div>
            </div>
          </div>
        </template>
      </OverviewCard>
    </template>
  </div>
</template>

<script setup lang="ts">
import OverviewCard from 'components/cards/OverviewCard.vue';
import { TGameOptionDto } from 'src/types';

defineProps<{
  options: TGameOptionDto[];
}>();

defineOptions({
  inheritAttrs: false,
});
</script>

<style scoped lang="scss">
.border-subtle {
  border: 1px solid rgba(0, 0, 0, 0.05);
}
</style>

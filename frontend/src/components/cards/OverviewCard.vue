<template>
  <q-card flat class="overview-card full-width">
    <q-card-section v-if="$slots.title || title" class="overview-card__header row items-center justify-between q-py-sm q-px-md">
      <div class="row items-center q-gutter-x-sm no-wrap">
        <q-icon v-if="icon" :name="icon" :color="iconColor || 'primary'" size="20px" />
        <div class="text-subtitle2 text-weight-bold text-dark">
          <slot name="title">{{ title }}</slot>
        </div>
      </div>
      <slot name="header-extra" />
    </q-card-section>
    <q-separator v-if="$slots.title || title" class="overview-card__separator" />
    <q-card-section class="overview-card__content q-pa-md">
      <slot name="content">
        <slot />
      </slot>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
defineProps<{
  title?: string;
  icon?: string;
  iconColor?: string;
}>();
</script>

<style scoped lang="scss">
.overview-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--kenner-border-color, rgba(0, 0, 0, 0.08));
  border-radius: var(--kenner-card-radius, 16px);
  overflow: hidden;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;

  &__header {
    background: rgba(0, 0, 0, 0.015);
    min-height: 44px;
  }

  &__separator {
    background: var(--kenner-border-color, rgba(0, 0, 0, 0.08));
  }
}
</style>

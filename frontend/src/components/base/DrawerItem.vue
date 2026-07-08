<template>
  <q-item
    :to="forwardName ? { name: forwardName } : undefined"
    @click="handleClick"
    clickable
    dense
    class="drawer-item q-mx-sm squircle-shape"
    active-class="drawer-item--active"
  >
    <q-item-section v-if="icon" avatar class="drawer-item__icon-section">
      <q-icon
        :name="icon"
        size="20px"
        :color="active ? (iconColor || 'primary') : (iconColor || 'grey-7')"
      />
    </q-item-section>
    <q-item-section v-else class="drawer-item__icon-section-empty" />
    <q-item-section class="drawer-item__text-section">
      <q-item-label class="drawer-item__label text-weight-medium">
        {{ label }}
      </q-item-label>
    </q-item-section>
  </q-item>
</template>

<script setup lang="ts">
import { inject } from 'vue';

type TKennerItem = {
  icon?: string;
  iconColor?: string;
  label: string;
  forwardName?: string;
  active?: boolean;
}
defineProps<TKennerItem>();
const emit = defineEmits(['click']);

const closeDrawer = inject('closeDrawer') as () => void;

function handleClick() {
  emit('click');
  if (closeDrawer) closeDrawer();
}
</script>

<style scoped lang="scss">
.drawer-item {
  min-height: 32px;
  padding: 2px 12px;
  margin: 1px 0;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
  color: #555;

  &.squircle-shape {
    border-radius: 8px !important;
  }

  &:hover {
    background: rgba(var(--q-primary), 0.05);
    color: var(--q-primary);

    .q-icon {
      color: var(--q-primary);
      transform: scale(1.05);
    }
  }

  &--active {
    background: linear-gradient(90deg, rgba(var(--q-primary), 0.1) 0%, rgba(var(--q-primary), 0.02) 100%);
    color: var(--q-primary);
    font-weight: 600;

    &::before {
      content: '';
      position: absolute;
      left: -8px;
      top: 15%;
      height: 70%;
      width: 4px;
      background: var(--q-primary);
      border-radius: 0 4px 4px 0;
    }
  }
}

.drawer-item__icon-section {
  min-width: 36px !important;
  padding-right: 0 !important;
  transition: transform 0.2s ease;
}

.drawer-item__icon-section-empty {
  min-width: 36px !important;
}

.drawer-item__text-section {
  padding-left: 8px;
}

.drawer-item__label {
  font-size: 0.9375rem;
  line-height: 1.2;
}
</style>

<template>
  <div class="smooth-switch" role="tablist">
    <div
      class="smooth-switch__thumb"
      :style="thumbStyle"
    />
    <button
      v-for="(opt, i) in options"
      :key="String(opt.value)"
      ref="btnRefs"
      type="button"
      role="tab"
      :aria-selected="isActive(opt.value)"
      class="smooth-switch__option"
      :class="{ 'is-active': isActive(opt.value) }"
      @click="select(opt.value, i)"
    >
      <q-icon v-if="opt.icon" :name="opt.icon" size="14px" class="q-mr-xs" />
      {{ opt.label }}
    </button>
  </div>
</template>

<script setup lang="ts" generic="T extends string | number | boolean">
import { computed, nextTick, onMounted, ref, watch } from 'vue';

interface Option {
  label: string;
  value: T;
  icon?: string;
}

const props = defineProps<{ options: Option[] }>();
const model = defineModel<T>({ required: true });

const btnRefs = ref<HTMLButtonElement[]>([]);
const thumbStyle = ref<Record<string, string>>({ opacity: '0' });

const activeIndex = computed(() =>
  props.options.findIndex((o) => o.value === model.value)
);

function isActive(v: T) {
  return model.value === v;
}

function select(v: T, _i: number) {
  model.value = v;
}

function updateThumb() {
  const idx = activeIndex.value;
  const el = btnRefs.value[idx];
  if (!el) {
    thumbStyle.value = { opacity: '0' };
    return;
  }
  thumbStyle.value = {
    transform: `translateX(${el.offsetLeft}px)`,
    width: `${el.offsetWidth}px`,
    opacity: '1',
  };
}

onMounted(() => {
  void nextTick(updateThumb);
  if (typeof ResizeObserver !== 'undefined') {
    const ro = new ResizeObserver(() => updateThumb());
    btnRefs.value.forEach((b) => b && ro.observe(b));
  }
  window.addEventListener('resize', updateThumb);
});

watch(
  () => [model.value, props.options.length],
  () => nextTick(updateThumb)
);
</script>

<style scoped lang="scss">
.smooth-switch {
  position: relative;
  display: inline-flex;
  align-items: stretch;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 999px;
  padding: 3px;
  user-select: none;
  line-height: 1;

  &__thumb {
    position: absolute;
    top: 3px;
    bottom: 3px;
    left: 0;
    border-radius: 999px;
    background: var(--q-primary);
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.18);
    transition: transform 260ms cubic-bezier(0.4, 0, 0.2, 1),
                width 260ms cubic-bezier(0.4, 0, 0.2, 1),
                opacity 200ms ease;
    z-index: 0;
    will-change: transform, width;
  }

  &__option {
    position: relative;
    z-index: 1;
    appearance: none;
    border: 0;
    background: transparent;
    cursor: pointer;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.2px;
    color: #6b7280;
    white-space: nowrap;
    transition: color 200ms ease;
    display: inline-flex;
    align-items: center;
    justify-content: center;

    &:hover:not(.is-active) {
      color: #374151;
    }

    &.is-active {
      color: #fff;
    }

    &:focus-visible {
      outline: 2px solid var(--q-primary);
      outline-offset: 2px;
    }
  }
}
</style>

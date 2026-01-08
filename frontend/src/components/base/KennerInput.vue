<template>
  <q-input
    :dark="dark"
    color="primary"
    v-model="modelValue"
    :label="label"
    lazy-rules
    :rules="rules"
    borderless
    dense
    class="kenner-input"
    v-bind="$attrs"
  >
    <template v-for="(_, slot) in $slots" #[slot]="scope">
      <slot :name="slot" v-bind="scope || {}" />
    </template>
  </q-input>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  rules?: any[],
  label?: string,
  dark?: boolean,
}>(), { dark: false });

const modelValue = defineModel();

</script>

<style lang="scss">
.kenner-input {
  background: rgba(0, 0, 0, 0.03);
  padding: 0 12px;
  border-radius: 6px;
  transition: all 0.3s ease;
  min-height: 36px;
  display: flex;
  align-items: center;
  border: 1px solid transparent;

  &:hover {
    background: rgba(0, 0, 0, 0.06);
  }

  &.q-field--focused {
    background: white;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    border: 1px solid rgba(54, 64, 88, 0.1);
  }

  .q-field__control {
    height: 36px !important;
    min-height: 36px !important;
    width: 100%;
  }

  .q-field__native, .q-field__prefix, .q-field__suffix, .q-field__input {
    font-weight: 600;
    color: var(--q-primary);
    padding: 0 !important;
  }

  .q-field__label {
    top: 18px !important;
    left: 12px !important;
    transform: translateY(-50%);
    transition: transform 0.3s, color 0.3s, font-size 0.3s;
    pointer-events: none;
  }

  &.q-field--float .q-field__label {
    transform: translateY(-130%) scale(0.75);
    background: white;
    padding: 0 4px;
    left: 8px !important;
    z-index: 10;
    border-radius: 4px;
    font-weight: 700;
  }

  &.q-field--error {
    border-color: var(--q-negative) !important;
    background: rgba(255, 0, 0, 0.03);

    .q-field__label {
      color: var(--q-negative) !important;
    }
  }

  .q-field__bottom {
    padding: 4px 0 0 !important;
  }
}
</style>

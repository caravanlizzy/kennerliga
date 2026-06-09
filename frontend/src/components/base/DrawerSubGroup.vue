<template>
  <q-item-label
    header
    class="text-primary text-weight-bolder text-uppercase q-px-md tracking-widest"
    style="font-size: 0.75rem; letter-spacing: 0.2em; opacity: 0.6; display: flex; align-items: center; padding-top: 8px; padding-bottom: 2px; min-height: 0; line-height: 1.2;"
  >
    <div style="height: 1px; flex-grow: 1; background: currentColor; opacity: 0.1; margin-right: 12px; display: none;"></div>
    <slot />
  </q-item-label>
</template>

<template>
  <q-item-label
    header
    class="text-primary text-weight-bolder text-uppercase q-pb-xs q-pt-md q-px-md tracking-widest"
    style="font-size: 0.7rem; letter-spacing: 0.2em; opacity: 0.6; display: flex; align-items: center;"
  >
    <div style="height: 1px; flex-grow: 1; background: currentColor; opacity: 0.1; margin-right: 12px; display: none;"></div>
    <slot />
  </q-item-label>
</template>

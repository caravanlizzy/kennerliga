<template>
  <q-tooltip
    class="kenner-tooltip bg-white text-dark rounded-borders shadow-6 q-px-sm q-py-xs text-caption"
    :delay="60"
    :hide-delay="120"
    anchor="top left"
    self="bottom left"
    transition-show="scale"
    transition-hide="fade"
    :offset="[8, 8]"
  >
    <div class="row items-center no-wrap q-gutter-x-xs">
      <slot />
    </div>
  </q-tooltip>
</template>


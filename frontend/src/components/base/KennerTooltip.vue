<template>
  <q-tooltip
    class="bg-white text-primary"
    :delay="50"
    :hide-delay="170"
    anchor="top left"
  >
    <slot/>
  </q-tooltip>
</template>

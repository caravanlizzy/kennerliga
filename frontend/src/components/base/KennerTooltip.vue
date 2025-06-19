<template>
  <q-tooltip
    class="kenner-tooltip"
    :delay="50"
    :hide-delay="170"
    anchor="top left"
  >
    <slot />
  </q-tooltip>
</template>

<style scoped>
.kenner-tooltip {
  background-color: white;
  color: #444;
  border-radius: 8px;
  box-shadow:
    0 2px 4px rgba(0, 0, 0, 0.08),
    0 4px 10px rgba(0, 0, 0, 0.04);
  font-size: 0.75rem;
  font-weight: 500;
  padding: 6px 10px;
  transition: all 0.2s ease-in-out;
}
</style>

<template>
  <div class="no-games-container q-pa-lg text-center">
    <q-icon name="search_off" size="48px" color="grey-4" class="q-mb-sm" />
    <div class="text-subtitle2 text-grey-6 font-weight-600">No games found</div>
    <div class="text-caption text-grey-5">Try adjusting your filters or search term</div>
  </div>
</template>

<style scoped>
.no-games-container {
  grid-column: 1 / -1;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 12px;
  border: 1px dashed rgba(0, 0, 0, 0.1);
}
.font-weight-600 {
  font-weight: 600;
}
</style>

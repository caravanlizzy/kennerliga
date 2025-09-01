<template>
  <div class="row items-center justify-end q-gutter-sm action-bar">
    <slot />
  </div>
</template>

<style scoped lang="scss">
.action-bar {
  padding: 8px 12px;
  background-color: #fafafa;       /* light background */
  border: 3px solid $primary;      /* thick, colorful border */
  border-radius: 10px;             /* rounded corners */
}
</style>

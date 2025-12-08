<template>
  <div class="row full-width full-height">
    <!-- Left -->
    <div class="col-12 col-md-6 split-left">
      <slot name="left">
        <slot />
      </slot>
    </div>

    <!-- Right -->
    <div class="col-12 col-md-6 split-right">
      <slot name="right" />
    </div>
  </div>
</template>

<style scoped>
/* Desktop and above */
@media (min-width: 1024px) {
  .split-left {
    padding-right: 8px;   /* q-pr-sm equivalent */
    margin-bottom: 8px;   /* q-mb-sm equivalent */
  }

  .split-right {
    padding-left: 8px;    /* q-pl-sm equivalent */
  }
}

/* Mobile: no margins, no padding → default (do nothing) */
</style>

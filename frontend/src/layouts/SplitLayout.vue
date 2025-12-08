<template>
  <div class="row full-width full-height split-container">
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
/* -----------------------------
   DESKTOP (>= 1024px)
------------------------------*/
@media (min-width: 1024px) {
  .split-container {
    position: relative;
  }

  /* Add separator line */
  .split-container::after {
    content: "";
    position: absolute;
    top: 0;
    bottom: 0;
    left: 50%;            /* exactly between the two columns */
    width: 1px;
    background: rgba(0, 0, 0, 0.1); /* subtle line */
    transform: translateX(-0.5px);  /* perfect centering */
  }

  .split-left {
    padding-right: 8px;
    margin-bottom: 8px;
  }

  .split-right {
    padding-left: 8px;
  }
}

/* -----------------------------
   MOBILE: no padding, no separator
------------------------------*/
@media (max-width: 1023px) {
  .split-container::after {
    display: none;
  }
}
</style>

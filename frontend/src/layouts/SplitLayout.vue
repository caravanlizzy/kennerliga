<template>
  <div class="row full-width full-height">
    <!-- Left -->
    <div class="col-12 col-md-6 q-pr-sm q-mb-sm q-mb-md-0">
      <slot name="left">
        <slot />
      </slot>
    </div>

    <!-- Right -->
    <div class="col-12 col-md-6 q-pl-sm">
      <slot name="right" />
    </div>
  </div>
</template>

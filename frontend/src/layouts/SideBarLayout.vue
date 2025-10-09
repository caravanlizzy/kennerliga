<!-- SideBarLayout.vue -->
<template>
  <div class="row no-wrap items-stretch">
    <div class="col min-w-0">
      <slot />
    </div>
    <q-separator vertical/>
    <div class="col-auto" style="width:300px; flex:0 0 auto">
      <slot name="side" />
    </div>
  </div>
</template>

<style scoped>
.min-w-0 { min-width: 0; } /* lets children be full-width without overflow fighting */
</style>

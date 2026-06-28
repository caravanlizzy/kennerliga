<template>
  <div class="purpose-block">
    <div class="row items-center no-wrap q-mb-xs">
      <q-icon name="emoji_objects" size="16px" color="grey-6" class="q-mr-xs" />
      <div class="text-caption text-weight-medium text-grey-7 text-uppercase purpose-block__title">What is KennerLiga?</div>
    </div>
    <p class="text-caption text-grey-7 q-mb-none">
      KennerLiga is a private space for our boardgame league. We organize seasons,
      auto-assign leagues, manage game picking, banning and results, and keep
      everyone in sync with chat and live updates.
    </p>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'PurposeSection' });
</script>

<style scoped>
.purpose-block__title {
  letter-spacing: 0.06em;
}
</style>

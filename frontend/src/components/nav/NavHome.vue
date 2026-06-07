<template>
  <div class="row items-center no-wrap">
    <KennerButton
      :to="{ name: 'home' }"
      unelevated
      flat
      color="dark"
      :class="[isMobile ? 'q-px-xs' : 'q-px-md', 'text-weight-bold']"
      style="height: 44px; min-width: 44px;"
    >
      <div class="row items-center no-wrap brand-wrap">
        <q-icon
          name="img:icons/favicon.svg"
          class="brand-k-icon"
          :class="{ 'brand-k-icon--mobile': isMobile }"
        />
        <span
          v-if="!isMobile"
          class="text-h5 text-weight-bold tracking-tight brand-text"
        ><span class="brand-text__word">enner</span><span class="brand-text__word">Liga</span></span>
      </div>
    </KennerButton>

  </div>
</template>
<script setup lang="ts">
import { useResponsive } from 'src/composables/responsive';
import KennerButton from 'components/base/KennerButton.vue';

const { isMobile } = useResponsive();

</script>

<style scoped lang="scss">
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@600;700;800&display=swap');

.brand-wrap {
  line-height: 1;
  text-transform: none;
}

:deep(.q-btn__content) {
  text-transform: none;
}

.brand-k-icon {
  font-size: 2rem;
  height: 2rem;
  width: 2rem;
  margin-right: -1px;
  position: relative;
  top: 1px;
}

.brand-k-icon--mobile {
  margin-right: 0;
}

.brand-text {
  font-family: 'Outfit', 'Segoe UI', system-ui, sans-serif;
  font-weight: 600;
  letter-spacing: 0.01em;
  line-height: 1;
  font-size: 1.5rem;
}

.brand-text__word {
  color: #1a2233;
}

:global(.body--dark) .brand-text__word {
  color: #f1f5f9;
}
</style>

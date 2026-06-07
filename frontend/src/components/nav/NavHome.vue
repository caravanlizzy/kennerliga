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
        <svg
          class="brand-k-icon"
          :class="{ 'brand-k-icon--mobile': isMobile }"
          viewBox="0 0 1024 1024"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
          focusable="false"
        >
          <defs>
            <linearGradient id="brandKGradient" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stop-color="#ff7a59" />
              <stop offset="100%" stop-color="#ec4899" />
            </linearGradient>
          </defs>
          <path
            d="M512 0L955.5 256V768L512 1024L68.5 768V256L512 0Z"
            fill="url(#brandKGradient)"
          />
          <path
            d="M380 320V704"
            stroke="#ffffff"
            stroke-width="80"
            stroke-linecap="round"
            fill="none"
          />
          <path
            d="M680 320L440 512L680 704"
            stroke="#ffffff"
            stroke-width="80"
            stroke-linecap="round"
            stroke-linejoin="round"
            fill="none"
          />
        </svg>
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
  display: inline-block;
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

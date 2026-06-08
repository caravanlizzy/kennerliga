<template>
  <div class="row items-center no-wrap brand-wrap" :class="{ 'brand-wrap--compact': compact }">
    <svg
      class="brand-k-icon"
      :class="{ 'brand-k-icon--compact': compact }"
      :style="{ width: iconSize, height: iconSize, fontSize: iconSize }"
      viewBox="0 0 1024 1024"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <defs>
        <linearGradient :id="gradientId" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#ff7a59" />
          <stop offset="100%" stop-color="#ec4899" />
        </linearGradient>
      </defs>
      <path
        d="M512 0L955.5 256V768L512 1024L68.5 768V256L512 0Z"
        :fill="`url(#${gradientId})`"
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
      v-if="!compact"
      class="brand-text"
      :style="{ fontSize: wordSize }"
    ><span class="brand-text__word">enner</span><span class="brand-text__word">Liga</span></span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    compact?: boolean;
    iconSize?: string;
    wordSize?: string;
  }>(),
  {
    compact: false,
    iconSize: '2rem',
    wordSize: '1.5rem',
  }
);

// unique gradient id per component instance to avoid SVG <defs> collisions
const uid = Math.random().toString(36).slice(2, 9);
const gradientId = computed(() => `brandKGradient-${uid}`);
void props;
</script>

<style scoped lang="scss">
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@600;700;800&display=swap');

.brand-wrap {
  line-height: 1;
  text-transform: none;
}

.brand-k-icon {
  display: inline-block;
  margin-right: -1px;
  position: relative;
  top: 1px;
}

.brand-k-icon--compact {
  margin-right: 0;
}

.brand-text {
  font-family: 'Outfit', 'Segoe UI', system-ui, sans-serif;
  font-weight: 600;
  letter-spacing: 0.01em;
  line-height: 1;
}

.brand-text__word {
  color: #1a2233;
}

:global(.body--dark) .brand-text__word {
  color: #f1f5f9;
}
</style>

<template>
  <svg
    class="avatar-shape-svg-defs"
    width="0"
    height="0"
    style="position: absolute; width: 0; height: 0; pointer-events: none; overflow: hidden;"
    aria-hidden="true"
  >
    <defs>
      <!-- Heart -->
      <clipPath id="avatar-clip-heart" clipPathUnits="objectBoundingBox">
        <path
          d="M 0.5,0.88 C 0.12,0.60 0.02,0.38 0.02,0.25 C 0.02,0.11 0.12,0.02 0.27,0.02 C 0.37,0.02 0.46,0.08 0.5,0.17 C 0.54,0.08 0.63,0.02 0.73,0.02 C 0.88,0.02 0.98,0.11 0.98,0.25 C 0.98,0.38 0.88,0.60 0.5,0.88 Z"
        />
      </clipPath>

      <!-- Shield -->
      <clipPath id="avatar-clip-shield" clipPathUnits="objectBoundingBox">
        <path
          d="M 0.08,0.05 L 0.92,0.05 C 0.92,0.05 0.96,0.56 0.5,0.97 C 0.04,0.56 0.08,0.05 0.08,0.05 Z"
        />
      </clipPath>

      <!-- Clover -->
      <clipPath id="avatar-clip-clover" clipPathUnits="objectBoundingBox">
        <path
          d="M 0.5,0.32 C 0.5,0.12 0.36,0.03 0.23,0.12 C 0.1,0.22 0.14,0.41 0.32,0.5 C 0.14,0.59 0.1,0.78 0.23,0.88 C 0.36,0.97 0.5,0.88 0.5,0.68 C 0.5,0.88 0.64,0.97 0.77,0.88 C 0.9,0.78 0.86,0.59 0.68,0.5 C 0.86,0.41 0.9,0.22 0.77,0.12 C 0.64,0.03 0.5,0.12 0.5,0.32 Z"
        />
      </clipPath>

      <!-- Star -->
      <clipPath id="avatar-clip-star" clipPathUnits="objectBoundingBox">
        <polygon
          points="0.5,0.02 0.63,0.35 0.98,0.35 0.7,0.57 0.81,0.92 0.5,0.71 0.19,0.92 0.3,0.57 0.02,0.35 0.37,0.35"
        />
      </clipPath>

      <!-- Diamond -->
      <clipPath id="avatar-clip-diamond" clipPathUnits="objectBoundingBox">
        <polygon points="0.5,0.02 0.98,0.5 0.5,0.98 0.02,0.5" />
      </clipPath>

      <!-- Hexagon -->
      <clipPath id="avatar-clip-hexagon" clipPathUnits="objectBoundingBox">
        <polygon points="0.5,0.02 0.95,0.25 0.95,0.75 0.5,0.98 0.05,0.75 0.05,0.25" />
      </clipPath>

      <!-- Octagon -->
      <clipPath id="avatar-clip-octagon" clipPathUnits="objectBoundingBox">
        <polygon
          points="0.29,0.02 0.71,0.02 0.98,0.29 0.98,0.71 0.71,0.98 0.29,0.98 0.02,0.71 0.02,0.29"
        />
      </clipPath>

      <!-- Badge (8-pointed star burst) -->
      <clipPath id="avatar-clip-badge" clipPathUnits="objectBoundingBox">
        <polygon
          points="0.5,0.02 0.64,0.14 0.85,0.15 0.86,0.36 0.98,0.5 0.86,0.64 0.85,0.85 0.64,0.86 0.5,0.98 0.36,0.86 0.15,0.85 0.14,0.64 0.02,0.5 0.14,0.36 0.15,0.15 0.36,0.14"
        />
      </clipPath>
    </defs>
  </svg>
</template>

<script setup lang="ts">
// Static SVG clip-path definitions for custom avatar shapes
</script>

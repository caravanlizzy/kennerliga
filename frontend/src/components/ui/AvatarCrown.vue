<template>
  <svg
    class="avatar-crown-svg"
    viewBox="0 0 32 32"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <defs>
      <linearGradient
        :id="goldGradientId"
        x1="4"
        y1="4"
        x2="28"
        y2="28"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0%" stop-color="#FFF9C4" />
        <stop offset="25%" stop-color="#FCD34D" />
        <stop offset="65%" stop-color="#F59E0B" />
        <stop offset="100%" stop-color="#D97706" />
      </linearGradient>
      <linearGradient
        :id="bandGradientId"
        x1="4"
        y1="22"
        x2="28"
        y2="28"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0%" stop-color="#F59E0B" />
        <stop offset="50%" stop-color="#D97706" />
        <stop offset="100%" stop-color="#B45309" />
      </linearGradient>
    </defs>

    <!-- Main Crown Body -->
    <path
      d="M5 23 L6.5 9.5 L12 15 L16 5 L20 15 L25.5 9.5 L27 23 Z"
      :fill="`url(#${goldGradientId})`"
      stroke="#B45309"
      stroke-width="1.2"
      stroke-linejoin="round"
    />
    <!-- Crown Base Band -->
    <path
      d="M4.5 22.5 C 10 24.5, 22 24.5, 27.5 22.5 L 27.5 25.5 C 22 27.5, 10 27.5, 4.5 25.5 Z"
      :fill="`url(#${bandGradientId})`"
      stroke="#92400E"
      stroke-width="1"
      stroke-linejoin="round"
    />
    <!-- Peak Jewels -->
    <circle
      cx="16"
      cy="5"
      r="2.2"
      fill="#FEF08A"
      stroke="#B45309"
      stroke-width="0.9"
    />
    <circle
      cx="6.5"
      cy="9.5"
      r="1.8"
      fill="#FEF08A"
      stroke="#B45309"
      stroke-width="0.9"
    />
    <circle
      cx="25.5"
      cy="9.5"
      r="1.8"
      fill="#FEF08A"
      stroke="#B45309"
      stroke-width="0.9"
    />
    <!-- Base Band Gems -->
    <circle
      cx="16"
      cy="24.8"
      r="1.4"
      fill="#EF4444"
      stroke="#991B1B"
      stroke-width="0.5"
    />
    <circle
      cx="10"
      cy="24.4"
      r="1.1"
      fill="#3B82F6"
      stroke="#1E40AF"
      stroke-width="0.5"
    />
    <circle
      cx="22"
      cy="24.4"
      r="1.1"
      fill="#10B981"
      stroke="#065F46"
      stroke-width="0.5"
    />
  </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const instanceId = Math.random().toString(36).substring(2, 9);
const goldGradientId = computed(() => `crown-gold-grad-${instanceId}`);
const bandGradientId = computed(() => `crown-band-grad-${instanceId}`);
</script>

<style scoped>
.avatar-crown-svg {
  width: 100%;
  height: 100%;
  display: block;
  overflow: visible;
}
</style>

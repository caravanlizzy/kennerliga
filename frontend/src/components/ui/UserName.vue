<template>
  <q-avatar
    :size="size"
    class="flex flex-center text-weight-medium"
    :class="shapeClass"
    :style="faceStyle"
    role="img"
    @click="router.push({ name: 'user-detail', params: { username: displayUsername } })"
  >
    <span class="mono" :class="textClass">{{ initials }}</span>
  </q-avatar>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  displayUsername: string
  size?: string
  maxLetters?: 1 | 2
  shape?: 'circle' | 'rounded' | 'squircle'
  border?: boolean
}>(), {
  size: '32px',
  maxLetters: 2,
  shape: 'rounded',
  border: false,
})

/* initials */
const clean = computed(() => (props.displayUsername ?? '').trim())
const parts = computed(() => clean.value.split(/\s+/).filter(Boolean))
const initials = computed(() => {
  const name = clean.value
  if (!name) return ''
  if (props.maxLetters === 1) return (parts.value[0]?.[0] ?? name[0]).toUpperCase()
  if (parts.value.length >= 2) return (parts.value[0][0] + (parts.value.at(-1)?.[0] ?? '')).toUpperCase()
  return name.slice(0, 2).toUpperCase()
})

/* deterministic color */
function hash(str: string) {
  let h = 0; for (let i = 0; i < str.length; i++) { h = (h << 5) - h + str.charCodeAt(i); h |= 0 }
  return Math.abs(h)
}
const hue = computed(() => hash(clean.value || 'user') % 360)
const sat = 55
const light = 70

const textClass = computed(() => (light >= 65 ? 'text-dark' : 'text-white'))
const borderColor = computed(() => `hsl(${hue.value} ${sat}% ${Math.max(light - 18, 35)}%)`)
const faceStyle = computed(() => ({
  background: `hsl(${hue.value} ${sat}% ${light}%)`,
  border: props.border ? `1px solid ${borderColor.value}` : 'none'
} as Record<string, string>))

/* shape */
const shapeClass = computed(() => {
  switch (props.shape) {
    case 'circle': return 'rounded-lg'
    case 'squircle': return 'squircle-shape'
    default: return 'rounded-borders'
  }
})
</script>

<style scoped>
.mono {
  line-height: 1;
  letter-spacing: 0.2px;
  font-size: 0.78rem;
  user-select: none;
}

/* squircle magic: quadratic border radius ratio */
.squircle-shape {
  border-radius: 25% / 35%;
}
</style>

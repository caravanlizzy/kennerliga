<template>
  <q-avatar
    :size="size"
    class="user-avatar"
    :class="shapeClass"
    :style="avatarStyle"
    :square="shape === 'rounded' || shape === 'squircle'"
    role="img"
    @click="router.push({ name: 'user-detail', params: { username: displayUsername } })"
  >
    <div class="avatar-inner full-width full-height flex flex-center">
      <span class="avatar-text">{{ initials }}</span>
    </div>
    <q-tooltip>{{ displayUsername }}</q-tooltip>
    <slot />
  </q-avatar>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const props = withDefaults(defineProps<{
  displayUsername: string
  size?: string
  maxLetters?: 1 | 2
  shape?: 'circle' | 'rounded' | 'squircle'
  border?: boolean
}>(), {
  size: '32px',
  maxLetters: 2,
  shape: 'squircle',
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


const avatarStyle = computed(() => {
  const baseHue = hue.value;
  const borderColor = `hsla(${baseHue}, ${sat}%, ${Math.max(light - 20, 40)}%, 0.6)`;
  const textColor = `hsl(${baseHue}, ${sat}%, ${Math.max(light - 30, 30)}%)`;

  return {
    '--avatar-border-color': borderColor,
    '--avatar-text-color': textColor,
    '--avatar-hue': baseHue.toString(),
    boxShadow: `0 2px 8px hsla(${baseHue}, ${sat}%, 20%, 0.05)`
  } as Record<string, string>
})

/* shape */
const shapeClass = computed(() => {
  switch (props.shape) {
    case 'circle': return '' // q-avatar is circular by default
    case 'squircle': return 'squircle-shape'
    default: return 'rounded-borders'
  }
})
</script>

<style scoped>
.user-avatar {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  cursor: pointer;
  border: 1px solid var(--avatar-border-color);
  color: var(--avatar-text-color);
}

.avatar-inner {
  border-radius: inherit;
}

.avatar-text {
  font-size: 0.85rem;
  font-weight: 600;
  line-height: 1;
  letter-spacing: 0.5px;
  user-select: none;
  text-transform: uppercase;
}

/* squircle magic: quadratic border radius ratio */
.squircle-shape {
  border-radius: 35% !important;
}
</style>

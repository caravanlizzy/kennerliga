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
      <span class="avatar-text" :style="textStyle">{{ initials }}</span>
    </div>

    <KennerTooltip v-if="displayUsername">
      <div class="column items-center">
        <div class="row items-center no-wrap q-mb-xs">
          <q-icon name="account_circle" size="18px" class="q-mr-xs text-primary opacity-80" />
          <span class="text-weight-bold text-dark text-body2">{{ displayUsername }}</span>
        </div>
        <div v-if="subtitle" class="text-caption text-grey-7 italic">
          {{ subtitle }}
        </div>
      </div>
    </KennerTooltip>

    <slot />
  </q-avatar>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import KennerTooltip from 'components/base/KennerTooltip.vue'

const router = useRouter()

const props = withDefaults(defineProps<{
  displayUsername: string
  subtitle?: string
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
const sat = 70
const light = 45

const avatarStyle = computed(() => {
  const baseHue = hue.value;
  const bgColor = `hsla(${baseHue}, ${sat}%, ${light}%, 0.85)`;
  const borderColor = `hsla(${baseHue}, ${sat}%, ${Math.max(light - 10, 20)}%, 0.2)`;
  const textColor = '#ffffff';

  return {
    '--avatar-bg-color': bgColor,
    '--avatar-border-color': borderColor,
    '--avatar-text-color': textColor,
    backgroundColor: bgColor,
    boxShadow: `0 2px 8px hsla(${baseHue}, ${sat}%, 20%, 0.1)`
  } as Record<string, string>
})

const textStyle = computed(() => {
  // Simple heuristic for font-size based on avatar size
  const numericSize = parseFloat(props.size || '32');
  const fontSize = numericSize * 0.42;
  return {
    fontSize: `${fontSize}px`
  }
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
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.opacity-80 {
  opacity: 0.8;
}

.user-avatar:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
  border-color: rgba(0, 0, 0, 0.1);
}

.avatar-inner {
  border-radius: inherit;
  transition: background-color 0.25s ease;
}

.avatar-text {
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.01em;
  user-select: none;
  text-transform: uppercase;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  opacity: 1;
}

/* squircle magic: proportional border radius */
.squircle-shape {
  border-radius: 28% !important;
}
</style>

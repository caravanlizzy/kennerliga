<template>
  <q-avatar
    :size="size"
    class="user-avatar"
    :class="[
      shapeClass,
      {
        'user-avatar--bordered': border,
        'user-avatar--navigable': canNavigate,
      },
    ]"
    :style="avatarStyle"
    :square="resolvedShape !== 'circle'"
    :role="canNavigate ? 'link' : 'img'"
    :tabindex="canNavigate ? 0 : undefined"
    :aria-label="
      canNavigate ? `View ${displayUsername}'s profile` : displayUsername
    "
    @click="navigate"
    @keydown.enter.prevent="navigate"
    @keydown.space.prevent="navigate"
  >
    <div class="avatar-inner full-width full-height flex flex-center">
      <span class="avatar-text" :style="textStyle">{{ initials }}</span>
    </div>

    <KennerTooltip v-if="displayUsername" :color="avatarStyle.backgroundColor">
      <div class="column items-center">
        <div class="row items-center no-wrap q-mb-xs">
          <q-icon
            name="account_circle"
            size="18px"
            class="q-mr-xs text-primary opacity-80"
          />
          <span class="text-weight-bold text-dark text-body2">{{
            displayUsername
          }}</span>
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
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import { type AvatarShape, getContrastTextColor } from 'src/types/avatar';

const router = useRouter();

const props = withDefaults(
  defineProps<{
    displayUsername: string;
    navigationName?: string;
    subtitle?: string;
    size?: string;
    maxLetters?: 1 | 2;
    shape?: AvatarShape | 'rounded' | string;
    color?: string;
    border?: boolean;
  }>(),
  {
    size: '32px',
    maxLetters: 2,
    shape: 'squircle',
    color: '',
    border: false,
  }
);

const navigationUserName = computed(
  () => props.navigationName ?? props.displayUsername
);
const canNavigate = computed(() => Boolean(navigationUserName.value?.trim()));

function navigate() {
  if (!canNavigate.value) return;
  router.push({
    name: 'user-detail',
    params: { username: navigationUserName.value },
  });
}

/* initials */
const clean = computed(() => (props.displayUsername ?? '').trim());
const parts = computed(() => clean.value.split(/\s+/).filter(Boolean));
const initials = computed(() => {
  const name = clean.value;
  if (!name) return '';
  if (props.maxLetters === 1)
    return (parts.value[0]?.[0] ?? name[0]).toUpperCase();
  if (parts.value.length >= 2)
    return (parts.value[0][0] + (parts.value.at(-1)?.[0] ?? '')).toUpperCase();
  return name.slice(0, 2).toUpperCase();
});

type AvatarColor = {
  background: string;
  hover: string;
  foreground: string;
};

const AVATAR_COLORS: readonly AvatarColor[] = [
  { background: '#dc2626', hover: '#b91c1c', foreground: '#ffffff' },
  { background: '#e11d48', hover: '#be123c', foreground: '#ffffff' },
  { background: '#f43f5e', hover: '#e11d48', foreground: '#ffffff' },
  { background: '#f05924', hover: '#d9481a', foreground: '#ffffff' },
  { background: '#f97316', hover: '#ea580c', foreground: '#1f2937' },
  { background: '#fb923c', hover: '#f97316', foreground: '#1f2937' },
  { background: '#f59e0b', hover: '#d97706', foreground: '#1f2937' },
  { background: '#eab308', hover: '#ca8a04', foreground: '#1f2937' },
  { background: '#facc15', hover: '#eab308', foreground: '#1f2937' },
  { background: '#84cc16', hover: '#65a30d', foreground: '#1f2937' },
  { background: '#a3e635', hover: '#84cc16', foreground: '#1f2937' },
  { background: '#22c55e', hover: '#16a34a', foreground: '#1f2937' },
  { background: '#10b981', hover: '#059669', foreground: '#1f2937' },
  { background: '#14b8a6', hover: '#0f766e', foreground: '#1f2937' },
  { background: '#2dd4bf', hover: '#14b8a6', foreground: '#1f2937' },
  { background: '#06b6d4', hover: '#0891b2', foreground: '#1f2937' },
  { background: '#38bdf8', hover: '#0ea5e9', foreground: '#1f2937' },
  { background: '#0ea5e9', hover: '#0284c7', foreground: '#1f2937' },
  { background: '#2563eb', hover: '#1d4ed8', foreground: '#ffffff' },
  { background: '#4f46e5', hover: '#4338ca', foreground: '#ffffff' },
  { background: '#6366f1', hover: '#4f46e5', foreground: '#ffffff' },
  { background: '#7c3aed', hover: '#6d28d9', foreground: '#ffffff' },
  { background: '#8b5cf6', hover: '#7c3aed', foreground: '#ffffff' },
  { background: '#a855f7', hover: '#9333ea', foreground: '#ffffff' },
  { background: '#c026d3', hover: '#a21caf', foreground: '#ffffff' },
  { background: '#d946ef', hover: '#c026d3', foreground: '#ffffff' },
  { background: '#db2777', hover: '#be185d', foreground: '#ffffff' },
  { background: '#ec4899', hover: '#db2777', foreground: '#ffffff' },
  { background: '#e879a9', hover: '#ec4899', foreground: '#1f2937' },
  { background: '#fb7185', hover: '#f43f5e', foreground: '#1f2937' },
];

function hash(value: string) {
  let result = 0;
  for (let index = 0; index < value.length; index += 1) {
    result = (result << 5) - result + value.charCodeAt(index);
    result |= 0;
  }
  return result >>> 0;
}

const avatarColor = computed<AvatarColor>(() => {
  if (props.color && props.color.trim()) {
    const rawColor = props.color.trim();
    const matched = AVATAR_COLORS.find(
      (c) => c.background.toLowerCase() === rawColor.toLowerCase()
    );
    if (matched) return matched;

    if (rawColor.startsWith('#')) {
      const fg = getContrastTextColor(rawColor);
      return {
        background: rawColor,
        hover: rawColor,
        foreground: fg,
      };
    }
  }

  return AVATAR_COLORS[
    hash(clean.value.toLocaleLowerCase() || 'user') % AVATAR_COLORS.length
  ];
});

const avatarStyle = computed(() => {
  const color = avatarColor.value;
  return {
    '--avatar-bg-color': color.background,
    '--avatar-border-color': color.hover,
    '--avatar-text-color': color.foreground,
    '--avatar-hover-bg': color.hover,
    backgroundColor: color.background,
  } as Record<string, string>;
});

/* shape */
const resolvedShape = computed<AvatarShape>(() => {
  const shapeProp = props.shape;
  if (!shapeProp || shapeProp === 'rounded') return 'squircle';
  return shapeProp as AvatarShape;
});

const shapeClass = computed(() => `shape-${resolvedShape.value}`);

const textStyle = computed(() => {
  const numericSize = parseFloat(props.size || '32');
  let factor = 0.42;
  const s = resolvedShape.value;
  if (s !== 'circle' && s !== 'squircle') {
    factor = 0.35;
  }
  const fontSize = numericSize * factor;
  return {
    fontSize: `${fontSize}px`,
  };
});
</script>

<style scoped>
.user-avatar {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid transparent;
  color: var(--avatar-text-color);
  background-color: var(--avatar-bg-color);
  box-shadow: none;
  transition: background-color 0.15s ease, border-color 0.15s ease, transform 0.15s ease;
}

.user-avatar--bordered {
  border-color: var(--avatar-border-color);
}

.user-avatar--navigable {
  cursor: pointer;
}

.user-avatar--navigable:focus-visible {
  outline: 3px solid color-mix(in srgb, var(--avatar-border-color), white 35%);
  outline-offset: 2px;
}

.opacity-80 {
  opacity: 0.8;
}

.user-avatar:hover {
  background-color: var(--avatar-hover-bg) !important;
}

.avatar-inner {
  border-radius: inherit;
}

.avatar-text {
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.01em;
  user-select: none;
  text-transform: uppercase;
  opacity: 1;
}

/* Shape definitions */
.shape-circle {
  border-radius: 50% !important;
}

.shape-squircle {
  border-radius: var(--kenner-card-radius, 8px) !important;
}

.shape-heart {
  clip-path: url(#avatar-clip-heart);
}

.shape-heart .avatar-inner {
  padding-bottom: 8%;
}

.shape-star {
  clip-path: url(#avatar-clip-star);
}

.shape-hexagon {
  clip-path: url(#avatar-clip-hexagon);
}

.shape-shield {
  clip-path: url(#avatar-clip-shield);
}

.shape-shield .avatar-inner {
  padding-bottom: 6%;
}

.shape-clover {
  clip-path: url(#avatar-clip-clover);
}

.shape-meeple {
  clip-path: url(#avatar-clip-meeple);
}

.shape-beetle {
  clip-path: url(#avatar-clip-beetle);
}

.shape-fish {
  clip-path: url(#avatar-clip-fish);
}

.shape-snake {
  clip-path: url(#avatar-clip-snake);
}

.shape-crown {
  clip-path: url(#avatar-clip-crown);
}

.shape-crown .avatar-inner {
  padding-top: 8%;
}

.shape-cat {
  clip-path: url(#avatar-clip-cat);
}

.shape-cat .avatar-inner {
  padding-top: 6%;
}

.shape-bear {
  clip-path: url(#avatar-clip-bear);
}

.shape-bear .avatar-inner {
  padding-top: 4%;
}

.shape-fox {
  clip-path: url(#avatar-clip-fox);
}

.shape-fox .avatar-inner {
  padding-top: 4%;
}

.shape-rabbit {
  clip-path: url(#avatar-clip-rabbit);
}

.shape-rabbit .avatar-inner {
  padding-top: 10%;
}

.shape-frog {
  clip-path: url(#avatar-clip-frog);
}

.shape-frog .avatar-inner {
  padding-top: 4%;
}

.shape-owl {
  clip-path: url(#avatar-clip-owl);
}

.shape-owl .avatar-inner {
  padding-top: 4%;
}

.shape-butterfly {
  clip-path: url(#avatar-clip-butterfly);
}

.shape-turtle {
  clip-path: url(#avatar-clip-turtle);
}
</style>

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
    :square="shape === 'rounded' || shape === 'squircle'"
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

const router = useRouter();

const props = withDefaults(
  defineProps<{
    displayUsername: string;
    navigationName?: string;
    subtitle?: string;
    size?: string;
    maxLetters?: 1 | 2;
    shape?: 'circle' | 'rounded' | 'squircle';
    border?: boolean;
  }>(),
  {
    size: '32px',
    maxLetters: 2,
    shape: 'squircle',
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
  { background: '#e11d48', hover: '#be123c', foreground: '#ffffff' },
  { background: '#f97316', hover: '#ea580c', foreground: '#1f2937' },
  { background: '#eab308', hover: '#ca8a04', foreground: '#1f2937' },
  { background: '#84cc16', hover: '#65a30d', foreground: '#1f2937' },
  { background: '#10b981', hover: '#059669', foreground: '#1f2937' },
  { background: '#06b6d4', hover: '#0891b2', foreground: '#1f2937' },
  { background: '#2563eb', hover: '#1d4ed8', foreground: '#ffffff' },
  { background: '#7c3aed', hover: '#6d28d9', foreground: '#ffffff' },
  { background: '#c026d3', hover: '#a21caf', foreground: '#ffffff' },
  { background: '#db2777', hover: '#be185d', foreground: '#ffffff' },
];

function hash(value: string) {
  let result = 0;
  for (let index = 0; index < value.length; index += 1) {
    result = (result << 5) - result + value.charCodeAt(index);
    result |= 0;
  }
  return result >>> 0;
}

const avatarColor = computed(
  () =>
    AVATAR_COLORS[
      hash(clean.value.toLocaleLowerCase() || 'user') % AVATAR_COLORS.length
    ]
);

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

const textStyle = computed(() => {
  // Simple heuristic for font-size based on avatar size
  const numericSize = parseFloat(props.size || '32');
  const fontSize = numericSize * 0.42;
  return {
    fontSize: `${fontSize}px`,
  };
});

/* shape */
const shapeClass = computed(() => {
  switch (props.shape) {
    case 'circle':
      return ''; // q-avatar is circular by default
    case 'squircle':
      return 'squircle-shape';
    default:
      return 'rounded-borders';
  }
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
  transition: background-color 0.15s ease, border-color 0.15s ease;
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

/* squircle magic: proportional border radius */
.squircle-shape {
  border-radius: var(--kenner-card-radius, 0px) !important;
}
</style>

<template>
  <q-badge
    v-if="badge"
    :color="getLeagueColor(Number(level))"
    class="text-weight-bold"
    v-bind="$attrs"
  >
    L{{ level }}
  </q-badge>
  <q-chip
    v-else-if="chip"
    :color="getLeagueColor(Number(level))"
    text-color="white"
    class="text-weight-bold"
    v-bind="$attrs"
  >
    L{{ level }}
  </q-chip>
  <div
    v-else
    class="league-level-shape flex flex-center relative-position"
    :style="computedStyle"
    v-bind="$attrs"
  >
    <span class="league-level-shape__prefix">L</span>
    <span class="league-level-shape__number">{{ level }}</span>
    <KennerTooltip>League {{ level }}</KennerTooltip>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { leagueColors } from 'src/composables/leagueColors';
import KennerTooltip from 'components/base/KennerTooltip.vue';

defineOptions({
  inheritAttrs: false,
});

interface Props {
  level: number | string;
  shape?: boolean;
  badge?: boolean;
  chip?: boolean;
  size?: string;
  fontSize?: string;
}

const props = withDefaults(defineProps<Props>(), {
  shape: false,
  badge: false,
  chip: false,
  size: '36px',
  fontSize: '',
});

const { getLeagueColor } = leagueColors();

const computedStyle = computed(() => {
  const sizeVal = props.size || '36px';
  const numericSize = parseFloat(sizeVal);
  const calculatedFontSize =
    props.fontSize || (numericSize ? `${Math.round(numericSize * 0.44)}px` : '14px');
  const calculatedRadius = numericSize
    ? `${Math.max(4, Math.min(8, Math.round(numericSize * 0.22)))}px`
    : '6px';

  return {
    width: sizeVal,
    height: sizeVal,
    fontSize: calculatedFontSize,
    borderRadius: calculatedRadius,
  };
});
</script>

<style scoped lang="scss">
.league-level-shape {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  user-select: none;
  vertical-align: middle;
  box-sizing: border-box;
  border: 1.5px solid #334155;
  color: #334155;
  background: rgba(51, 65, 85, 0.04);
  line-height: 1;

  &__prefix {
    font-size: 0.72em;
    font-weight: 600;
    opacity: 0.72;
    margin-right: 1px;
    letter-spacing: 0.02em;
    pointer-events: none;
  }

  &__number {
    font-size: 1em;
    font-weight: 800;
    letter-spacing: -0.02em;
    pointer-events: none;
  }
}
</style>

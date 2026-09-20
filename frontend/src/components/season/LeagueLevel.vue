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
    class="league-level-shape flex flex-center"
    :style="computedStyle"
    v-bind="$attrs"
  >
    L{{ level }}
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { leagueColors } from 'src/composables/leagueColors';

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

const { getLeagueColor, getLeagueTheme } = leagueColors();

const computedStyle = computed(() => {
  const sizeVal = props.size || '36px';
  const numericSize = parseFloat(sizeVal);
  const calculatedFontSize =
    props.fontSize || (numericSize ? `${Math.round(numericSize * 0.48)}px` : '15px');
  const calculatedRadius = numericSize
    ? `${Math.max(4, Math.min(8, Math.round(numericSize * 0.22)))}px`
    : '6px';

  const theme = getLeagueTheme(Number(props.level) || 1);

  return {
    width: sizeVal,
    height: sizeVal,
    fontSize: calculatedFontSize,
    borderRadius: calculatedRadius,
    background: theme.bg,
    color: theme.text,
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
  border: none;
  font-weight: 700;
  line-height: 1;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.01em;
}
</style>

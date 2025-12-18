<template>
  <div
    :class="bordered ? `border-2 rounded-borders border-${color}` : ''"
    class="q-mt-xs"
  >
    <template v-if="expandable">
      <q-expansion-item
        v-model="isOpened"
        dense-toggle
        expand-separator
        expand-icon="expand_more"
        expanded-icon="expand_less"
        :expand-icon-class="`text-${color}`"
        :expanded-icon-class="`text-${color}`"
        :header-class="`text-${color} text-h5 q-py-xs justify-center with-opacity`"
      >
        <template #header>
          <div class="full-width row justify-center items-center">
            {{ title }}
          </div>
        </template>
        <q-separator inset :color="color" />
        <div>
          <slot />
        </div>
      </q-expansion-item>
    </template>
    <template v-else>
      <div
        class="full-width row q-pr-lg items-center text-h5 q-py-xs"
        :class="[`text-${color}`, titleEnd ? 'justify-end' : 'justify-center']"
      >
        {{ title }}
      </div>
      <q-separator inset :color="color" />
      <slot />
    </template>
  </div>
</template>

<script setup lang="ts">

const isOpened = defineModel<boolean>('isOpened', { default: true });

withDefaults(
  defineProps<{
    title: string;
    color: string;
    bordered?: boolean;
    titleEnd?: boolean;
    expandable?: boolean;
  }>(),
  {
    titleEnd: false,
    expandable: false,
    bordered: true,
  }
);
</script>

<!-- ActionBar.vue -->
<script setup lang="ts">
import { useActionBar } from 'src/composables/actionBar';
import KennerButton from 'components/base/KennerButton.vue';

const { actions, description } = useActionBar();


</script>

<template>
  <!-- full-width wrapper so we can center the inner bar -->
  <div class="actionBar-wrap q-px-sm q-my-md">
    <div class="row justify-between items-center actionBar bg-white q-py-xs q-px-lg">
      <div class="text-h6">Action</div>

      <div class="text-body2 text-grey-7">
        <component v-if="description" :is="description" />
      </div>

      <div class="row items-center no-wrap q-gutter-sm">
        <kenner-button
          dense
          flat
          :color="a.buttonColor || 'primary'"
          v-for="a in actions"
          :key="a.name"
          @click="a.callback"
        >
          {{ a.name }}
        </kenner-button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.actionBar-wrap {
  width: 100%;
}

/* The “action area” — full width on mobile, constrained & centered on desktop */
.actionBar {
  border: 3px solid $info;
  width: min(100%, 1040px);   /* cap width on large screens */
  margin-inline: auto;        /* center horizontally */
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(0,0,0,.06);
}

/* You can bump the cap a bit more on very wide displays if you like */
@media (min-width: 1440px) {
  .actionBar {
    width: min(100%, 700px);
  }
}
</style>

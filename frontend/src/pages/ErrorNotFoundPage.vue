<template>
  <div class="fullscreen bg-grey-1 text-center q-pa-md flex flex-center column">
    <!-- Error code -->
    <div class="text-h2 text-accent text-bold">
      {{ code }}
    </div>

    <!-- Message -->
    <div class="text-h5 q-mt-md">
      {{ message }}
    </div>

    <!-- Extra description -->
    <div v-if="description" class="text-subtitle1 q-mt-sm text-grey-7">
      {{ description }}
    </div>

    <!-- Actions -->
    <KennerButton
      class="q-mt-xl"
      color="positive"
      icon="home"
      label="Go Home"
      to="/"
      size="lg"
    />
  </div>
</template>

<script setup lang="ts">
import KennerButton from 'components/base/KennerButton.vue';

defineProps({
  code: {
    type: [String, Number],
    default: 404
  },
  message: {
    type: String,
    default: 'Oops! Page not found.'
  },
  description: {
    type: String,
    default: 'The page you are looking for doesn’t exist.'
  }
});
</script>

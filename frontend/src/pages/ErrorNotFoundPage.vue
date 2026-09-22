<template>
  <div class="fullscreen flex flex-center q-pa-md notfound-bg">
    <q-card flat class="notfound-card text-center q-pa-xl column items-center">
      <BrandLogo class="q-mb-lg" icon-size="48px" word-size="1.75rem" />

      <div class="notfound-code text-primary q-my-sm">
        {{ code }}
      </div>

      <div class="text-h5 text-weight-bolder text-dark q-mt-xs">
        {{ message }}
      </div>

      <div v-if="description" class="text-body2 text-grey-6 q-mt-sm" style="max-width: 360px">
        {{ description }}
      </div>

      <div class="q-mt-xl">
        <KennerButton
          color="primary"
          icon="home"
          label="Return Home"
          to="/"
          size="md"
          class="shadow-2"
        />
      </div>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import BrandLogo from 'components/base/BrandLogo.vue';
import KennerButton from 'components/base/KennerButton.vue';

defineProps({
  code: {
    type: [String, Number],
    default: 404,
  },
  message: {
    type: String,
    default: 'Page Not Found',
  },
  description: {
    type: String,
    default: 'The page you are looking for does not exist or has moved.',
  },
});
</script>

<style scoped lang="scss">
.notfound-bg {
  background: radial-gradient(circle at 50% 30%, rgba(54, 64, 88, 0.05) 0%, rgba(245, 245, 247, 1) 100%);
}

.notfound-card {
  max-width: 480px;
  width: 100%;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--kenner-border-color, rgba(0, 0, 0, 0.08));
  border-radius: var(--kenner-card-radius, 20px);
}

.notfound-code {
  font-size: 5rem;
  font-weight: 900;
  line-height: 1;
  letter-spacing: -2px;
}
</style>
